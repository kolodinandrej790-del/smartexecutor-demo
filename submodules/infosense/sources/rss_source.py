# infosense/sources/rss_source.py — RSS-парсер новостей.
# Роль: получать события из RSS-фидов (CoinDesk, Cointelegraph, The Block).
# Версия 1.0.

import feedparser
import time
from datetime import datetime, timezone
from typing import List

# Импортируем контракт Event
import sys
sys.path.insert(0, ".")
from core.contracts import Event

# Импортируем классификатор
from submodules.infosense.keywords import classify_event, get_impact, extract_asset


# ========== КОНФИГ ФИДОВ ==========
FEEDS = [
    {
        "name": "coindesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "source_type": "secondary",
    },
    {
        "name": "cointelegraph",
        "url": "https://cointelegraph.com/rss",
        "source_type": "secondary",
    },
    {
        "name": "theblock",
        "url": "https://www.theblock.co/rss.xml",
        "source_type": "secondary",
    },
]

# Известные активы для извлечения
KNOWN_ASSETS = ["BTC", "ETH", "XAUT", "PAXG", "LTC", "SOL", "XRP", "BNB", "ADA", "DOGE"]

# Ограничение новостей из одного фида
MAX_ITEMS_PER_FEED = 10

# Кэш (TTL 5 минут)
_cache = {
    "events": None,
    "ts": 0,
}
CACHE_TTL_SECONDS = 300


def _parse_date(entry) -> int:
    """Извлекает timestamp из entry RSS."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            pass
    return int(time.time())


def fetch_rss(feed: dict) -> List[Event]:
    """
    Парсит один RSS-фид.
    Возвращает список Event.
    """
    events = []
    try:
        parsed = feedparser.parse(feed["url"])
        entries = parsed.entries[:MAX_ITEMS_PER_FEED]

        for entry in entries:
            headline = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")

            # Объединяем текст для анализа
            text = f"{headline} {summary}"

            event_type = classify_event(text)
            impact = get_impact(text)
            asset = extract_asset(text, KNOWN_ASSETS)

            events.append(Event(
                ts=_parse_date(entry),
                source=feed["name"],
                source_type=feed["source_type"],
                type=event_type,
                asset=asset,
                impact=impact,
                confidence="MEDIUM",  # для RSS — средняя (это пересказ)
                headline=headline,
                url=url,
                market_reaction=None,
                raw={"summary": summary[:200]},
            ))
    except Exception:
        pass  # тихо — если один фид упал, остальные работают

    return events


def fetch_all_feeds(force_refresh: bool = False) -> List[Event]:
    """
    Парсит все фиды из конфига.
    Возвращает объединённый список Event.
    """
    now = int(time.time())

    # Проверка кэша
    if not force_refresh and _cache["events"] is not None:
        if now - _cache["ts"] < CACHE_TTL_SECONDS:
            return _cache["events"]

    all_events = []
    for feed in FEEDS:
        events = fetch_rss(feed)
        all_events.extend(events)

    # Сортировка по времени (новые — сверху)
    all_events.sort(key=lambda e: e.ts, reverse=True)

    # Обновляем кэш
    _cache["events"] = all_events
    _cache["ts"] = now

    return all_events


def clear_cache():
    """Сбрасывает кэш — для тестов."""
    _cache["events"] = None
    _cache["ts"] = 0