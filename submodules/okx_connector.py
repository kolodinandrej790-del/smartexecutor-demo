# okx_connector.py — Финальная версия + журнал сделок + библиотека уроков

import requests
import json
import base64
import hmac
import hashlib
import time
import os
from datetime import datetime, timezone


class OKXConnector:
    def __init__(self, api_key, secret_key, passphrase):
        self.base_url = "https://www.okx.com"
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        print(f"OKX коннектор создан для ключа: {self.api_key[:8]}...")

    def _sign(self, timestamp, method, request_path, body=""):
        message = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()

    def _request_signed(self, method, endpoint, params=None):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + str(int(datetime.now(timezone.utc).microsecond/1000)).zfill(3) + "Z"

        if params is None:
            params = {}

        if method == "GET":
            query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            request_path = endpoint + ("?" + query_string if query_string else "")
            body = ""
        else:
            request_path = endpoint
            body = json.dumps(params) if params else ""

        signature = self._sign(timestamp, method, request_path, body)

        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

        url = self.base_url + request_path
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            else:
                resp = requests.post(url, headers=headers, data=body, timeout=10)
            return resp.json()
        except Exception as e:
            print(f"Сетевой сбой (signed): {e}")
            return {"code": "-1", "msg": str(e)}

    def _request_public(self, endpoint, params=None):
        url = self.base_url + endpoint
        try:
            resp = requests.get(url, params=params, timeout=10)
            return resp.json()
        except Exception as e:
            print(f"Сетевой сбой (public): {e}")
            return {"code": "-1", "msg": str(e)}

    # ========== БАЛАНС ==========
    def get_balance(self, ccy=None):
        params = {}
        if ccy:
            params["ccy"] = ccy
        return self._request_signed("GET", "/api/v5/account/balance", params)

    # ========== РЫНОЧНЫЕ ДАННЫЕ ==========
    def get_ticker(self, symbol):
        return self._request_public("/api/v5/market/ticker", {"instId": symbol})

    def get_klines(self, symbol, bar="5m", limit=20):
        return self._request_public("/api/v5/market/candles", {
            "instId": symbol, "bar": bar, "limit": limit
        })

    def get_orderbook(self, symbol, sz=10):
        return self._request_public("/api/v5/market/books", {
            "instId": symbol, "sz": sz
        })

    # ========== ТОРГОВЛЯ ==========
    def place_order(self, symbol, side, qty, order_type="market", stop_loss=None, take_profit=None):
        params = {
            "instId": symbol,
            "tdMode": "cash",
            "side": side.lower(),
            "ordType": order_type,
            "sz": str(qty)
        }
        if stop_loss:
            params["slTriggerPx"] = str(stop_loss)
        if take_profit:
            params["tpTriggerPx"] = str(take_profit)

        return self._request_signed("POST", "/api/v5/trade/order", params)

    # ========== ЖУРНАЛ СДЕЛОК ==========
    def log_trade(self, symbol, side, entry, stop, take, status):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date, time_str = now.split(" ")

        log_line = f"| {date} | {time_str} | {symbol} | {side} | {entry} | {stop} | {take} | {status} |\n"

        with open("trade_log.md", "a", encoding="utf-8") as f:
            f.write(log_line)

    # ========== БИБЛИОТЕКА УРОКОВ ==========
    def log_lesson(self, symbol, side, entry, exit_price, profit, reason):
        lesson = {
            "symbol": symbol,
            "side": side,
            "entry": entry,
            "exit": exit_price,
            "profit": profit,
            "reason": reason,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if os.path.exists("lessons.json"):
            with open("lessons.json", "r", encoding="utf-8") as f:
                try:
                    lessons = json.load(f)
                except:
                    lessons = []
        else:
            lessons = []

        lessons.append(lesson)

        with open("lessons.json", "w", encoding="utf-8") as f:
            json.dump(lessons, f, ensure_ascii=False, indent=2)

        print(f"Урок записан: {reason}")

    # ========== СБОР ДАННЫХ ДЛЯ АГЕНТА ==========
    def gather_market_data(self, symbol, level):
        ticker_resp = self.get_ticker(symbol)
        if ticker_resp.get("code") != "0":
            return None

        ticker_data = ticker_resp["data"][0]
        price = float(ticker_data["last"])

        klines_resp = self.get_klines(symbol, bar="5m", limit=10)
        if klines_resp.get("code") != "0":
            return None

        candles = klines_resp["data"]
        volumes = [float(c[5]) for c in candles]
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]

        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        current_volume = volumes[-1] if volumes else 0

        wick_above = max(highs[-3:]) if highs else price
        wick_below = min(lows[-3:]) if lows else price

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
            "liquidity_above": 0,
            "atr": atr
        }