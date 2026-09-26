# cmc_connector.py — Коннектор CoinMarketCap API
# Роль: обёртка над CMC API. Только сеть, без логики.
# Ключ передаётся в конструкторе. Никакого логирования (K-002).
# Версия 1.2: исправлен параметр issuer_id в get_rwa_issuer.

import requests


class CMCConnector:
    def __init__(self, api_key):
        self.base_url = "https://pro-api.coinmarketcap.com"
        self.api_key = api_key
        self.headers = {
            "X-CMC_PRO_API_KEY": api_key,
            "Accept": "application/json"
        }

    def _request(self, endpoint, params=None, max_retries=3):
        if params is None:
            params = {}
        url = self.base_url + endpoint
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=30)
                return resp.json()
            except Exception as e:
                last_error = str(e)
        return {"error": last_error}

    # ========== КРИПТОВАЛЮТЫ ==========
    def get_quotes(self, symbols):
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        return self._request("/v3/cryptocurrency/quotes/latest", {"symbol": symbols})

    def get_listings(self, limit=100):
        return self._request("/v3/cryptocurrency/listings/latest", {
            "limit": limit,
            "convert": "USD"
        })

    def get_market_pairs(self, symbol, matched_symbol="USDT", category="spot"):
        return self._request("/v2/cryptocurrency/market-pairs/latest", {
            "symbol": symbol,
            "matched_symbol": matched_symbol,
            "category": category,
            "aux": "effective_liquidity,market_score"
        })

    # ========== RWA (Real World Assets) ==========
    def get_rwa_issuers(self):
        """Список эмитентов токенизированных активов."""
        return self._request("/v5/real-world-assets/issuers/list")

    def get_rwa_issuer(self, issuer_id):
        """Токены конкретного эмитента. Параметр: issuer_id (не id!)."""
        return self._request("/v5/real-world-assets/issuers", {"issuer_id": issuer_id})

    # ========== FEAR & GREED ==========
    def get_fear_greed(self):
        url = "https://api.coinmarketcap.com/data-api/v3/fear-greed/historical"
        try:
            resp = requests.get(url, params={"limit": 1}, timeout=10)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}