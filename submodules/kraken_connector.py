# kraken_connector.py — Публичный API Kraken (только цены)
# Роль: get_price(symbol) для арбитража.
# Без ключей — публичные эндпоинты.
# Версия 1.0.

import requests


class KrakenConnector:
    def __init__(self):
        self.name = "kraken"
        self.base_url = "https://api.kraken.com"

    def get_price(self, symbol):
        """
        symbol: "XAUTUSD" (формат Kraken, без разделителя)
        Возвращает: {"price": float, "bid": float, "ask": float, "source": "kraken"} или None.
        """
        url = self.base_url + "/0/public/Ticker"
        try:
            r = requests.get(url, params={"pair": symbol}, timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            if data.get("error"):
                return None
            result = data.get("result", {})
            if not result:
                return None
            # Kraken возвращает ключ пары (может отличаться от запрошенного)
            pair_key = list(result.keys())[0]
            ticker = result[pair_key]
            # ticker["b"][0] = bid, ticker["a"][0] = ask, ticker["c"][0] = last
            bid = float(ticker["b"][0])
            ask = float(ticker["a"][0])
            return {
                "price": (bid + ask) / 2,
                "bid": bid,
                "ask": ask,
                "source": self.name
            }
        except Exception:
            return None