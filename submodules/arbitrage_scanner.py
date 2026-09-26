# arbitrage_scanner.py — Поиск арбитражных возможностей
# Роль: опрашивает источники, находит расхождения, даёт сигнал.
# Не знает о конкретных биржах — получает список источников (K-016).
# Версия 2.0: + внутрибиржевой арбитраж (spot vs linear).

class ArbitrageScanner:
    def __init__(self, sources):
        self.sources = sources

    # ========== МЕЖБИРЖЕВОЙ АРБИТРАЖ ==========
    def scan(self, asset, symbol_map, fee_percent=0.1, threshold=0.5):
        prices = {}

        for source in self.sources:
            source_name = getattr(source, "name", "unknown")
            symbol = symbol_map.get(source_name)
            if not symbol:
                continue

            result = source.get_price(symbol)
            if result and result.get("price"):
                prices[source_name] = {
                    "price": result["price"],
                    "bid": result["bid"],
                    "ask": result["ask"]
                }

        if len(prices) < 2:
            return {
                "asset": asset,
                "mode": "cross_exchange",
                "opportunity": False,
                "reason": "Меньше 2 источников с ценой",
                "prices": prices
            }

        best_buy = min(prices.items(), key=lambda x: x[1]["ask"])
        best_sell = max(prices.items(), key=lambda x: x[1]["bid"])

        buy_exchange, buy_data = best_buy
        sell_exchange, sell_data = best_sell

        buy_price = buy_data["ask"]
        sell_price = sell_data["bid"]

        spread_percent = (sell_price - buy_price) / buy_price * 100
        net_profit_percent = spread_percent - fee_percent * 2

        return {
            "asset": asset,
            "mode": "cross_exchange",
            "buy_at": buy_exchange,
            "buy_price": buy_price,
            "sell_at": sell_exchange,
            "sell_price": sell_price,
            "spread_percent": round(spread_percent, 4),
            "net_profit_percent": round(net_profit_percent, 4),
            "opportunity": net_profit_percent >= threshold,
            "threshold": threshold,
            "all_prices": prices
        }

    # ========== ВНУТРИБИРЖЕВОЙ АРБИТРАЖ (spot vs linear) ==========
    def scan_internal(self, asset, exchange, symbol, fee_percent=0.1, threshold=0.2):
        """
        exchange: коннектор с поддержкой category (Bybit).
        symbol: например "XAUTUSDT".
        """
        if not hasattr(exchange, "get_price"):
            return None

        try:
            spot = exchange.get_price(symbol, category="spot")
            linear = exchange.get_price(symbol, category="linear")
        except TypeError:
            # Коннектор не поддерживает category
            return None

        if not spot or not linear:
            return {
                "asset": asset,
                "mode": "internal",
                "opportunity": False,
                "reason": "Нет spot или linear данных",
                "exchange": getattr(exchange, "name", "unknown")
            }

        spot_price = spot["price"]
        linear_price = linear["price"]
        diff = linear_price - spot_price
        diff_percent = diff / spot_price * 100

        # Если linear дешевле spot — покупаем linear, продаём spot
        # Если linear дороже — наоборот
        abs_percent = abs(diff_percent)
        net = abs_percent - fee_percent  # одна биржа

        return {
            "asset": asset,
            "mode": "internal",
            "exchange": getattr(exchange, "name", "unknown"),
            "spot_price": spot_price,
            "linear_price": linear_price,
            "basis": round(diff, 4),
            "basis_percent": round(diff_percent, 4),
            "net_profit_percent": round(net, 4),
            "opportunity": net >= threshold,
            "threshold": threshold,
            "direction": "buy_linear_sell_spot" if diff < 0 else "buy_spot_sell_linear"
        }

    def scan_multi(self, assets, fee_percent=0.1, threshold=0.5):
        results = []
        for asset in assets:
            r = self.scan(asset["name"], asset["symbols"], fee_percent, threshold)
            results.append(r)
        return results