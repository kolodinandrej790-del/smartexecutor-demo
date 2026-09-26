# bybit_connector.py — Публичный API Bybit (только цены)
# Роль: get_price(symbol) для арбитража.
# Без ключей — публичные эндпоинты.
# Версия 2.0.
#
# ВНИМАНИЕ: старая версия 4.0 содержала:
#   - приватные методы (place_order, get_balance) — требуют ключи, сейчас не нужны;
#   - gather_market_data — перенесён в LevelBuilder (K-010);
#   - синтаксическую ошибку в _request (две команды в строке).
# Всё это вынесено. Оставлен только get_price.

import requests


class BybitConnector:
    def __init__(self):
        self.name = "bybit"
        self.base_url = "https://api.bybit.com"

    def get_price(self, symbol, category="spot"):
        """
        symbol: "XAUTUSDT" (без слэша, без дефиса)
        category: "spot" или "linear"
        Возвращает: {"price": float, "bid": float, "ask": float} или None.
        """
        url = self.base_url + "/v5/market/tickers"
        try:
            r = requests.get(url, params={"category": category, "symbol": symbol}, timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            if data.get("retCode") != 0:
                return None
            ticker = data["result"]["list"][0]
            bid = float(ticker["bid1Price"])
            ask = float(ticker["ask1Price"])
            return {
                "price": (bid + ask) / 2,
                "bid": bid,
                "ask": ask,
                "source": self.name
            }
        except Exception:
            return None