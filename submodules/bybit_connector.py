# bybit_connector.py v4.0 — Полный коннектор с рыночными данными

import requests
import json
import time
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


class BybitConnector:
    def __init__(self, api_key, private_key_path="private_key.pem", testnet=False):
        self.base_url = "https://api-demo.bybit.com" if testnet else "https://api.bybit.com"
        self.api_key = api_key

        with open(private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        print(f"Коннектор создан для API-ключа: {self.api_key[:8]}...")

    def _sign(self, payload):
        signature = self.private_key.sign(
            payload.encode(), padding.PKCS1v15(), hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    def _request(self, method, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))

        if params is None:
            params = {}
        params["timestamp"] = timestamp

        sorted_params = sorted(params.items())
        param_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        sign_payload = timestamp + self.api_key + param_string
        signature = self._sign(sign_payload)

        headers = {
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-SIGN": signature,
            "X-BAPI-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        if method == "GET":
            resp = requests.get(url, params=params, headers=headers)
        else:
            resp = requests.post(url, json=params, headers=headers)
        return resp.json()

    # ========== БАЛАНС И ОРДЕРА ==========
    def get_balance(self):
        return self._request("GET", "/v5/account/wallet-balance", {"accountType": "UNIFIED"})

    def place_order(self, symbol, side, qty, order_type="Market", stop_loss=None, take_profit=None):
        params = {
            "category": "linear",
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": str(qty)
        }
        if stop_loss:
            params["stopLoss"] = str(stop_loss)
        if take_profit:
            params["takeProfit"] = str(take_profit)
        return self._request("POST", "/v5/order/create", params)

    def get_positions(self, symbol=None):
        params = {"category": "linear", "settleCoin": "USDT"}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/v5/position/list", params)

    # ========== РЫНОЧНЫЕ ДАННЫЕ ==========
    def get_klines(self, symbol, interval="5", limit=50):
        """Свечи: interval = 1, 5, 15, 60, 240, D"""
        return self._request("GET", "/v5/market/kline", {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })

    def get_ticker(self, symbol):
        """Текущая цена"""
        return self._request("GET", "/v5/market/tickers", {
            "category": "linear",
            "symbol": symbol
        })

    def get_orderbook(self, symbol, limit=50):
        """Стакан"""
        return self._request("GET", "/v5/market/orderbook", {
            "category": "linear",
            "symbol": symbol,
            "limit": limit
        })

    def get_instruments(self, category="linear"):
        """Список инструментов"""
        return self._request("GET", "/v5/market/instruments-info", {"category": category})

    # ========== СБОР ДАННЫХ ДЛЯ АГЕНТА ==========
    def gather_market_data(self, symbol, level):
        """Собирает пакет данных для TraderSense и стратегий"""
        # Текущая цена
        ticker = self.get_ticker(symbol)
        if ticker.get("retCode") != 0:
            return None
        
        ticker_data = ticker["result"]["list"][0]
        price = float(ticker_data["lastPrice"])
        high_24h = float(ticker_data["highPrice24h"])
        low_24h = float(ticker_data["lowPrice24h"])
        volume_24h = float(ticker_data["volume24h"])

        # Свечи для объёма и шипов
        klines = self.get_klines(symbol, interval="5", limit=10)
        if klines.get("retCode") != 0:
            return None

        candles = klines["result"]["list"]
        volumes = [float(c[5]) for c in candles]
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]
        
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        current_volume = volumes[-1] if volumes else 0
        
        # Шип над уровнем
        wick_above = max(highs[-3:]) if highs else price
        wick_below = min(lows[-3:]) if lows else price
        
        # ATR (упрощённо: размах за 5 свечей)
        ranges = [highs[i] - lows[i] for i in range(len(highs))]
        atr = sum(ranges) / len(ranges) if ranges else 0

        return {
            "asset": symbol,
            "price": price,
            "level": level,
            "volume_current": current_volume,
            "volume_average": avg_volume,
            "wick_above_level": wick_above,
            "wick_below_level": wick_below,
            "liquidity_above": 0,  # будем запрашивать отдельно, если нужно
            "atr": atr
        }