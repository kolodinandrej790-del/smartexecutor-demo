# TradeArchive v1.0 — Пассивный журнал сделок

import json
import os
from datetime import datetime

class TradeArchive:
    def __init__(self, filepath="archive/trades.json"):
        self.filepath = filepath
        self.trades = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)

    def add(self, asset, direction, entry, stop_loss, take_profit, strategy, result=None, reason=""):
        trade = {
            "id": len(self.trades) + 1,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "asset": asset,
            "direction": direction,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "strategy": strategy,
            "result": result,
            "reason": reason
        }
        self.trades.append(trade)
        self._save()
        return trade["id"]

    def get_all(self):
        return self.trades

    def get_by_id(self, trade_id):
        for t in self.trades:
            if t["id"] == trade_id:
                return t
        return None

    def count(self):
        return len(self.trades)


# === ТЕСТ ===
if __name__ == "__main__":
    import tempfile
    # Создаём временный файл для теста
    test_file = "archive/test_trades.json"
    ta = TradeArchive(test_file)
    
    print("=== TradeArchive ТЕСТ ===")
    
    # Добавляем сделки
    id1 = ta.add("ETH/USDT", "SELL", 4500, 4550, 4400, "InstitutionalCore", None, "стоп-ран")
    id2 = ta.add("BTC/USDT", "BUY", 60000, 59000, 62000, "SwingCore", None, "тренд")
    print(f"Добавлены сделки: #{id1}, #{id2}")
    print(f"Всего сделок: {ta.count()}")
    
    # Ищем сделку
    trade = ta.get_by_id(1)
    print(f"Сделка #1: {trade['asset']} {trade['direction']} по {trade['entry']}")
    
    # Удаляем тестовый файл
    os.remove(test_file)
    print("Тест пройден, временный файл удалён")