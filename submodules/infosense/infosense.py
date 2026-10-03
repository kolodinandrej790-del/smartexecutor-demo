# infosense/infosense.py — Фасад InfoSense.
# Роль: единая точка входа для сбора рыночного контекста.
# Диспетчер знает только этот класс (K-002).
# Версия 1.0.

from typing import Optional, List, Dict, Any

import sys
sys.path.insert(0, ".")
from core.contracts import Event

from submodules.infosense.aggregator import (
    get_market_context as _get_market_context,
    get_all_events as _get_all_events,
)
from submodules.infosense.sources.fear_greed import get_fear_greed as _get_fear_greed


class InfoSense:
    """
    Фасад модуля InfoSense.
    Возвращает контекст рынка: события + bias + Fear & Greed.
    """

    def __init__(self):
        self.name = "infosense"

    def get_market_context(self,
                           asset: Optional[str] = None,
                           rss_window_minutes: int = 360,
                           exchange_window_minutes: int = 10080) -> Dict[str, Any]:
        """
        Возвращает рыночный контекст.
        asset: "BTC" | "ETH" | None (весь рынок).
        """
        return _get_market_context(
            asset=asset,
            rss_window_minutes=rss_window_minutes,
            exchange_window_minutes=exchange_window_minutes,
        )

    def get_events(self,
                   asset: Optional[str] = None,
                   rss_window_minutes: int = 360,
                   exchange_window_minutes: int = 10080) -> List[Event]:
        """
        Возвращает список событий.
        Если asset указан — фильтрует по активу + общие.
        """
        ctx = self.get_market_context(
            asset=asset,
            rss_window_minutes=rss_window_minutes,
            exchange_window_minutes=exchange_window_minutes,
        )
        return ctx["events"]

    def get_fear_greed(self) -> Optional[Dict[str, Any]]:
        """Возвращает Fear & Greed Index."""
        return _get_fear_greed()

    def get_bias(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Возвращает только bias_info (без событий)."""
        ctx = self.get_market_context(asset=asset)
        return ctx["bias_info"]