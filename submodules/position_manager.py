# position_manager.py — Сопровождение открытых позиций

import time


class PositionManager:
    def __init__(self, connector, symbol, qty, entry_price, take_profit, stop_loss, direction):
        self.connector = connector
        self.symbol = symbol
        self.qty = qty
        self.entry_price = entry_price
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.direction = direction  # "BUY" или "SELL"
        self.status = "OPEN"
        self.closed = False
        self.close_price = None

    def check(self):
        """Проверяет текущую цену и решает, закрывать ли позицию"""
        ticker = self.connector.get_ticker(self.symbol)
        if ticker.get("code") != "0":
            return self.status

        price = float(ticker["data"][0]["last"])

        if self.direction == "BUY":
            if price >= self.take_profit:
                self.status = "CLOSED_TP"
                self.close_price = price
                self.closed = True
            elif price <= self.stop_loss:
                self.status = "CLOSED_SL"
                self.close_price = price
                self.closed = True
        else:  # SELL
            if price <= self.take_profit:
                self.status = "CLOSED_TP"
                self.close_price = price
                self.closed = True
            elif price >= self.stop_loss:
                self.status = "CLOSED_SL"
                self.close_price = price
                self.closed = True

        return self.status

    def close_position(self):
        """Закрывает позицию на бирже"""
        if self.direction == "BUY":
            side = "sell"
        else:
            side = "buy"

        try:
            order = self.connector.place_order(
                symbol=self.symbol,
                side=side,
                qty=round(self.qty, 6)
            )
            return order
        except Exception as e:
            return {"error": str(e)}

    def status_text(self):
        return (
            f"[{self.symbol}] {self.direction} | "
            f"Вход: {self.entry_price:.2f} | "
            f"Тейк: {self.take_profit:.2f} | "
            f"Стоп: {self.stop_loss:.2f} | "
            f"Статус: {self.status}"
        )


# === ТЕСТ ===
if __name__ == "__main__":
    # Тест без подключения к бирже
    class MockConnector:
        def get_ticker(self, symbol):
            return {"code": "0", "data": [{"last": "2510"}]}

        def place_order(self, symbol, side, qty):
            return {"msg": "mock order"}

    pm = PositionManager(
        connector=MockConnector(),
        symbol="ETH-USDT",
        qty=0.002,
        entry_price=2500,
        take_profit=2550,
        stop_loss=2460,
        direction="BUY"
    )

    print(pm.status_text())
    print("Проверка позиции:", pm.check())