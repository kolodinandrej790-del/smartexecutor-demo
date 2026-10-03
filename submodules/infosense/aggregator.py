# infosense/aggregator.py — Агрегатор событий из всех источников.
# Роль: собирать, фильтровать, объединять события.
# Версия 1.2: расширены окна для реальных источников.

import time
from typing import List, Optional, Dict, Any

# Импорт контракта
import sys
sys.path.insert(0, ".")
from core.contracts import Event

# Импорт источников
from submodules.infosense.sources.fear_greed import get_fear_greed
from submodules.infosense.sources.rss_source import fetch_all_feeds
from submodules.infosense.sources.okx_announcements import fetch_all_announcements as fetch_okx
from submodules.infosense.sources.binance_announcements import fetch_all_announcements as fetch_binance


# ========== КОНФИГ ==========
DEFAULT_RSS_WINDOW_MINUTES = 360        # RSS: 6 часов
DEFAULT_EXCHANGE_WINDOW_MINUTES = 10080  # OKX/Binance: 7 дней


def get_all_events(rss_window_minutes: int = DEFAULT_RSS_WINDOW_MINUTES,
                   exchange_window_minutes: int = DEFAULT_EXCHANGE_WINDOW_MINUTES) -> List[Event]:
    """
    Собирает события из всех источников.
    Использует разные окна:
      - RSS (новости): rss_window_minutes.
      - Биржи (анонсы): exchange_window_minutes.
    """
    now = int(time.time())
    rss_cutoff = now - rss_window_minutes * 60
    exchange_cutoff = now - exchange_window_minutes * 60

    all_events = []

    # RSS
    try:
        rss_events = fetch_all_feeds()
        all_events.extend([e for e in rss_events if e.ts >= rss_cutoff])
    except Exception:
        pass

    # OKX
    try:
        okx_events = fetch_okx()
        all_events.extend([e for e in okx_events if e.ts >= exchange_cutoff])
    except Exception:
        pass

    # Binance
    try:
        binance_events = fetch_binance()
        all_events.extend([e for e in binance_events if e.ts >= exchange_cutoff])
    except Exception:
        pass

    all_events.sort(key=lambda e: e.ts, reverse=True)
    return all_events


def filter_by_asset(events: List[Event], asset: str) -> List[Event]:
    """Фильтрует события по активу. Оставляет также события для всего рынка."""
    if not asset:
        return events
    asset_upper = asset.upper()
    return [
        e for e in events
        if e.asset is None or e.asset.upper() == asset_upper
    ]


def compute_bias(events: List[Event]) -> Dict[str, Any]:
    """Вычисляет общий bias по событиям."""
    if not events:
        return {
            "bias": 0,
            "events_count": 0,
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "confidence": "LOW",
        }

    bias = sum(e.impact for e in events)
    bullish = sum(1 for e in events if e.impact > 0)
    bearish = sum(1 for e in events if e.impact < 0)
    neutral = sum(1 for e in events if e.impact == 0)

    if abs(bias) >= 10 and (bullish + bearish) >= 5:
        confidence = "HIGH"
    elif abs(bias) >= 3:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "bias": bias,
        "events_count": len(events),
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral,
        "confidence": confidence,
    }


def get_market_context(asset: Optional[str] = None,
                       rss_window_minutes: int = DEFAULT_RSS_WINDOW_MINUTES,
                       exchange_window_minutes: int = DEFAULT_EXCHANGE_WINDOW_MINUTES) -> Dict[str, Any]:
    """
    Возвращает рыночный контекст.
    """
    all_events = get_all_events(
        rss_window_minutes=rss_window_minutes,
        exchange_window_minutes=exchange_window_minutes,
    )

    if asset:
        events = filter_by_asset(all_events, asset)
    else:
        events = [e for e in all_events if e.asset is None]

    bias_info = compute_bias(events)
    fg = get_fear_greed()

    return {
        "asset": asset,
        "rss_window_minutes": rss_window_minutes,
        "exchange_window_minutes": exchange_window_minutes,
        "events": events[:30],
        "bias_info": bias_info,
        "fear_greed": fg,
        "ts": int(time.time()),
    }