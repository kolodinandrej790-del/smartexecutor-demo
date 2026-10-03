# infosense/sources/binance_announcements.py — Анонсы Binance.
# Роль: получать листинги и делистинги с Binance (primary-источник).
# API: https://www.binance.com/bapi/composite/v1/public/cms/article/list/query
# Версия 1.0.

import requests
import time
import re
from typing import List

# Импортируем контракт Event
import sys
sys.path.insert(0, ".")
from core.contracts import Event


# ========== КОНФИГ ==========
BASE_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"

# Категории Binance (catalogId)
CATEGORIES = [
    {"catalog_id": 48, "type": "listing", "impact": 3, "name": "New Cryptocurrency Listing"},
    {"catalog_id": 161, "type": "delisting", "impact": -3, "name": "Delisting"},
]

# Стоп-слова (котируемые валюты — не тикеры)
QUOTE_CURRENCIES = {"USDT", "USDC", "USD", "EUR", "BTC", "ETH", "BNB", "BUSD"}

# Кэш (TTL 5 минут)
_cache = {"events": None, "ts": 0}
CACHE_TTL_SECONDS = 300


def _is_valid_ticker(ticker: str) -> bool:
    """Проверяет, что тикер валиден."""
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
    Извлекает тикеры из заголовка анонса Binance.
    Примеры:
      "Binance Will List XYZ (XYZ)"
      "Binance Will Delist ABC"
      "Binance Adds XYZ on Spot"
    """
    if not title:
        return []

    assets = set()

    # Паттерн 1: (XXX) — тикер в скобках
    for match in re.finditer(r"\(([A-Z0-9]{2,10})\)", title):
        ticker = match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    # Паттерн 2: XXX/USDT или XXX/USD
    for match in re.finditer(r"\b([A-Z0-9]{2,10})/(?:USDT|USDC|USD|EUR|BTC|ETH|BNB)\b", title):
        ticker = match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    # Паттерн 3: "list XXX" / "delist XXX" / "adds XXX"
    action_match = re.search(
        r"\b(?:list|delist|adds?|launch(?:es)?|remove)\s+([A-Z0-9]{2,10})\b",
        title,
    )
    if action_match:
        ticker = action_match.group(1)
        if _is_valid_ticker(ticker):
            assets.add(ticker)

    return list(assets)


def _parse_timestamp(item: dict) -> int:
    """Извлекает timestamp из статьи Binance."""
    release_ms = item.get("releaseDate", 0)
    try:
        return int(release_ms) // 1000
    except Exception:
        return int(time.time())


def fetch_binance_category(cat_config: dict) -> List[Event]:
    """Получает одну категорию анонсов Binance."""
    events = []
    try:
        params = {
            "type": 1,
            "catalogId": cat_config["catalog_id"],
            "pageNo": 1,
            "pageSize": 20,
        }
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code != 200:
            return events

        data = r.json()
        if data.get("code") != "000000":
            return events

        catalogs = data.get("data", {}).get("catalogs", [])
        for group in catalogs:
            articles = group.get("articles", [])
            for article in articles:
                title = article.get("title", "")
                article_id = article.get("id")
                article_code = article.get("code", "")
                ts = _parse_timestamp(article)

                # Строим URL
                url = ""
                if article_code:
                    url = f"https://www.binance.com/en/support/announcement/{article_code}"

                assets = _extract_assets(title)
                asset = assets[0] if assets else None

                events.append(Event(
                    ts=ts,
                    source="binance_announcements",
                    source_type="primary",
                    type=cat_config["type"],
                    asset=asset,
                    impact=cat_config["impact"],
                    confidence="HIGH",
                    headline=title,
                    url=url,
                    market_reaction=None,
                    raw={
                        "catalog_id": cat_config["catalog_id"],
                        "catalog_name": cat_config["name"],
                        "article_id": article_id,
                        "all_assets": assets,
                    },
                ))
    except Exception:
        pass

    return events


def fetch_all_announcements(force_refresh: bool = False) -> List[Event]:
    """Получает все категории анонсов Binance."""
    now = int(time.time())

    if not force_refresh and _cache["events"] is not None:
        if now - _cache["ts"] < CACHE_TTL_SECONDS:
            return _cache["events"]

    all_events = []
    for cat in CATEGORIES:
        events = fetch_binance_category(cat)
        all_events.extend(events)

    all_events.sort(key=lambda e: e.ts, reverse=True)

    _cache["events"] = all_events
    _cache["ts"] = now

    return all_events


def clear_cache():
    """Сбрасывает кэш — для тестов."""
    _cache["events"] = None
    _cache["ts"] = 0