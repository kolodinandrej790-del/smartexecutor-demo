# okx_connector.py — Коннектор OKX
# Роль: связь с OKX. Подпись, публичные данные, баланс, торговля.
# Ключ передаётся в конструкторе. Никакого логирования (K-002).
# Версия 3.0: + get_price, + attachAlgoOrds, + retry, исправлен timestamp.

import requests
import json
import base64
import hmac
import hashlib
import time
from datetime import datetime, timezone


class OKXConnector:
    def __init__(self, api_key, secret_key, passphrase):
        self.name = "okx"
        self.base_url = "https://www.okx.com"
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    # ========== ПОДПИСЬ И ЗАПРОСЫ ==========
    def _sign(self, timestamp, method, request_path, body=""):
        message = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()

    def _timestamp(self):
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%dT%H:%M:%S.") + str(int(now.microsecond / 1000)).zfill(3) + "Z"

    def _request_signed(self, method, endpoint, params=None, max_retries=3):
        if params is None:
            params = {}

        if method == "GET":
            query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            request_path = endpoint + ("?" + query_string if query_string else "")
            body = ""
        else:
            request_path = endpoint
            body = json.dumps(params) if params else ""

        url = self.base_url + request_path
        last_error = None

        for attempt in range(max_retries):
            timestamp = self._timestamp()
            signature = self._sign(timestamp, method, request_path, body)
            headers = {
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json"
            }
            try:
                if method == "GET":
                    resp = requests.get(url, headers=headers, timeout=30)
                else:
                    resp = requests.post(url, headers=headers, data=body, timeout=30)
                return resp.json()
            except Exception as e:
                last_error = str(e)

        return {"code": "-1", "msg": last_error}

    def _request_public(self, endpoint, params=None, max_retries=3):
        url = self.base_url + endpoint
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, params=params, timeout=30)
                return resp.json()
            except Exception as e:
                last_error = str(e)
        return {"code": "-1", "msg": last_error}

    # ========== БАЛАНС ==========
    def get_balance(self, ccy=None):
        params = {}
        if ccy:
            params["ccy"] = ccy
        return self._request_signed("GET", "/api/v5/account/balance", params)

    # ========== РЫНОЧНЫЕ ДАННЫЕ ==========
    def get_ticker(self, symbol):
        return self._request_public("/api/v5/market/ticker", {"instId": symbol})

    def get_price(self, symbol):
        """
        symbol: "XAUT-USDT" (формат OKX, с дефисом)
        Возвращает: {"price": float, "bid": float, "ask": float, "source": "okx"} или None.
        """
        try:
            r = self.get_ticker(symbol)
            if r.get("code") != "0":
                return None
            data = r["data"][0]
            bid = float(data.get("bidPx", 0) or 0)
            ask = float(data.get("askPx", 0) or 0)
            last = float(data.get("last", 0) or 0)
            if bid == 0 or ask == 0:
                return {"price": last, "bid": last, "ask": last, "source": self.name}
            return {
                "price": (bid + ask) / 2,
                "bid": bid,
                "ask": ask,
                "source": self.name
            }
        except Exception:
            return None

    def get_klines(self, symbol, bar="5m", limit=20):
        return self._request_public("/api/v5/market/candles", {
            "instId": symbol, "bar": bar, "limit": limit
        })

    def get_orderbook(self, symbol, sz=10):
        return self._request_public("/api/v5/market/books", {
            "instId": symbol, "sz": sz
        })

    # ========== ТОРГОВЛЯ ==========
    def place_order(self, symbol, side, qty, order_type="market",
                    stop_loss=None, take_profit=None, td_mode="cash"):
        """
        Ордер на OKX.
        symbol: "XAUT-USDT"
        side: "buy" | "sell"
        order_type: "market" | "limit"
        td_mode: "cash" (спот) | "cross" | "isolated" (margin/futures)
        stop_loss / take_profit: числа или None
        SL/TP ставятся через attachAlgoOrds (R-022, D-001).
        """
        params = {
            "instId": symbol,
            "tdMode": td_mode,
            "side": side.lower(),
            "ordType": order_type,
            "sz": str(qty)
        }

        # SL/TP через attachAlgoOrds — работает на бирже, не симулируется
        if stop_loss or take_profit:
            algo = {}
            if take_profit:
                algo["tpTriggerPx"] = str(take_profit)
                algo["tpOrdPx"] = "-1"  # -1 = market по триггеру
                algo["tpTriggerPxType"] = "last"
            if stop_loss:
                algo["slTriggerPx"] = str(stop_loss)
                algo["slOrdPx"] = "-1"
                algo["slTriggerPxType"] = "last"
            params["attachAlgoOrds"] = [algo]

        return self._request_signed("POST", "/api/v5/trade/order", params)