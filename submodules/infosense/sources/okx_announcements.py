# infosense/sources/okx_announcements.py — Анонсы OKX.
# Роль: получать листинги и делистинги с OKX (primary-источник).
# API: https://www.okx.com/api/v5/support/announcements
# Версия 1.2: фикс миграций + улучшенное извлечение тикера + исключение чисел.

import requests
import time
import re
from typing import List

# Импортируем контракт Event
import sys
sys.path.insert(0, ".")
from core.contracts import Event


# ========== КОНФИГ ==========
BASE_URL = "https://www.okx.com/api/v5/support/announcements"

# Типы анонсов (только реальные)
ANN_TYPES = [
    {"type": "listing", "ann_type": "announcements-new-listings", "impact": 3},
    {"type": "delisting", "ann_type": "announcements-delistings", "impact": -3},
]

# Стоп-слова (не тикеры — это котируемые валюты)
QUOTE_CURRENCIES = {"USDT", "USDC", "USD", "EUR", "BTC", "ETH", "OKB"}

# Слова-признаки миграций (не листинг и не делистинг)
MIGRATION_WORDS = ["migration", "migrate", "token swap", "swap to", "token merger"]

# Кэш (TTL 5 минут)
_cache = {"events": None, "ts": 0}
CACHE_TTL_SECONDS = 300


def _is_migration(title: str) -> bool:
    """Проверяет, что анонс — про миграцию, а не листинг/делистинг."""
    if not title:
        return False
    title_lower = title.lower()
    return any(word in title_lower for word in MIGRATION_WORDS)


def _is_valid_ticker(ticker: str) -> bool:
    """
    Проверяет, что тикер валиден.
    Исключает: котируемые валюты, чистые числа, слишком короткие/длинные.
    """
    if not ticker:
        return False
    if ticker in QUOTE_CURRENCIES:
        return False
    if ticker.isdigit():
        return False
    if len(ticker) < 2 or len(ticker) > 10:
        return False
    return True


def _extract_assets(title: str) -> List[str]:
    """
    Извлекает тикеры из заголовка анонса.
    Возвращает список тикеров (может быть несколько).
    """
    if not title:
        return []

    assets = set()

    # Паттерн 1: XXX/USDT или XXX/USD (базовый актив перед /)
    for match in re.finditer(r"\b([A-Z0-9]{2,10})/(?:USDT|USDC|USD|EUR|BTC|ETH)\b", title):
        ticker = match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    # Паттерн 2: (XXX) в скобках — тикер
    for match in re.finditer(r"\(([A-Z0-9]{2,10})\)", title):
        ticker = match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    # Паттерн 3: "list XXX and YYY" или "list XXX, YYY"
    list_match = re.search(
        r"\blist(?:ing)?\s+([A-Z0-9]{2,10}(?:\s+(?:and|,)\s+[A-Z0-9]{2,10})*)",
        title,
    )
    if list_match:
        tickers_str = list_match.group(1)
        for ticker in re.findall(r"\b([A-Z0-9]{2,10})\b", tickers_str):
            if _is_valid_ticker(ticker):
                assets.add(ticker)

    # Паттерн 4: "support XXX crypto" или "support XXX token"
    support_match = re.search(r"\bsupport\s+([A-Z0-9]{2,10})\b", title)
    if support_match:
        ticker = support_match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    return list(assets)


def fetch_okx_announcements(ann_type_config: dict) -> List[Event]:
    """Получает один тип анонсов OKX."""
    events = []
    try:
        params = {
            "annType": ann_type_config["ann_type"],
            "limit": 20,
        }
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code != 200:
            return events

        data = r.json()
        if data.get("code") != "0":
            return events

        details_list = data.get("data", [])
        for group in details_list:
            details = group.get("details", [])
            for item in details:
                title = item.get("title", "")
                url = item.get("url", "")
                ptime_ms = int(item.get("pTime", 0))
                ptime_s = ptime_ms // 1000

                # Пропускаем миграции — они не листинг и не делистинг
                if _is_migration(title):
                    continue

                assets = _extract_assets(title)
                # Если тикеров несколько — берём первый (основной)
                asset = assets[0] if assets else None

                events.append(Event(
                    ts=ptime_s,
                    source="okx_announcements",
                    source_type="primary",
                    type=ann_type_config["type"],
                    asset=asset,
                    impact=ann_type_config["impact"],
                    confidence="HIGH",
                    headline=title,
                    url=url,
                    market_reaction=None,
                    raw={
                        "ann_type": ann_type_config["ann_type"],
                        "all_assets": assets,
                    },
                ))
    except Exception:
        pass

    return events


def fetch_all_announcements(force_refresh: bool = False) -> List[Event]:
    """Получает все типы анонсов OKX."""
    now = int(time.time())

    if not force_refresh and _cache["events"] is not None:
        if now - _cache["ts"] < CACHE_TTL_SECONDS:
            return _cache["events"]

    all_events = []
    for ann_type in ANN_TYPES:
        events = fetch_okx_announcements(ann_type)
        all_events.extend(events)

    all_events.sort(key=lambda e: e.ts, reverse=True)

    _cache["events"] = all_events
    _cache["ts"] = now

    return all_events


def clear_cache():
    """Сбрасывает кэш — для тестов."""
    _cache["events"] = None
    _cache["ts"] = 0