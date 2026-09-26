# binance_connector.py — Публичный API Binance (только цены)
# Роль: get_price(symbol) для арбитража.
# Без ключей — публичные эндпоинты.
# Версия 1.0.

import requests


class BinanceConnector:
    def __init__(self):
        self.name = "binance"
        self.base_url = "https://api.binance.com"

    def get_price(self, symbol):
        """
        symbol: "XAUTUSDT" (без слэша, без дефиса)
        Возвращает: {"price": float, "bid": float, "ask": float} или None.
        """
        url = self.base_url + "/api/v3/ticker/bookTicker"
        try:
            r = requests.get(url, params={"symbol": symbol}, timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            bid = float(data["bidPrice"])
            ask = float(data["askPrice"])
            return {
                "price": (bid + ask) / 2,
                "bid": bid,
                "ask": ask,
                "source": self.name
            }
        except Exception:
            return None