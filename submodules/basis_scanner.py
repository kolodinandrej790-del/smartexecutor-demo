# basis_scanner.py — Внутрибиржевой арбитраж (spot vs linear)
# Роль: ищет расхождения между спотом и фьючерсом на одной бирже.
# Не знает о конкретных биржах — получает источник с методом get_price(symbol, category).
# Версия 1.0.

class BasisScanner:
    def __init__(self, sources):
        """
        sources: список объектов с методом get_price(symbol, category) → {price, bid, ask, source} или None
        """
        self.sources = sources

    def scan(self, asset, symbol, categories=("spot", "linear"), fee_percent=0.1, threshold=0.5):
        """
        asset: "XAUT"
        symbol: "XAUTUSDT" (для Bybit/Binance)
        categories: кортеж категорий для сравнения
        fee_percent: комиссия одной биржи (taker)
        threshold: минимальный чистый профит, %

        Возвращает: dict с результатом.
        """
        results = []

        for source in self.sources:
            source_name = getattr(source, "name", "unknown")
            cat_prices = {}

            for cat in categories:
                try:
                    r = source.get_price(symbol, category=cat) if cat != "spot" else source.get_price(symbol)
                except TypeError:
                    # OKX-коннектор не принимает category
                    if cat != "spot":
                        continue
                    r = source.get_price(symbol)

                if r and r.get("price"):
                    cat_prices[cat] = {
                        "price": r["price"],
                        "bid": r["bid"],
                        "ask": r["ask"]
                    }

            if len(cat_prices) < 2:
                continue

            # Внутрибиржевой базис: купить дешевле, продать дороже
            buy_cat = min(cat_prices.items(), key=lambda x: x[1]["ask"])
            sell_cat = max(cat_prices.items(), key=lambda x: x[1]["bid"])

            buy_price = buy_cat[1]["ask"]
            sell_price = sell_cat[1]["bid"]

            spread_percent = (sell_price - buy_price) / buy_price * 100
            # Комиссия: одна биржа, две сделки (открыть + закрыть)
            net_profit_percent = spread_percent - fee_percent * 2

            results.append({
                "exchange": source_name,
                "asset": asset,
                "buy_at": f"{source_name}/{buy_cat[0]}",
                "buy_price": buy_price,
                "sell_at": f"{source_name}/{sell_cat[0]}",
                "sell_price": sell_price,
                "spread_percent": round(spread_percent, 4),
                "net_profit_percent": round(net_profit_percent, 4),
                "opportunity": net_profit_percent >= threshold,
                "threshold": threshold
            })

        return results