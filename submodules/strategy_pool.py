# StrategyPool v1.0 — Контейнер стратегий

from submodules.institutional_core import InstitutionalCore
from submodules.trader_sense import TraderSense


class StrategyPool:
    def __init__(self, mode="lite", active_strategies=None):
        self.mode = mode
        self.trader_sense = TraderSense()

        # Доступные стратегии
        self.strategies = {
            "institutional": InstitutionalCore(mode=mode),
            # "scalper": ScalperCore(),
            # "day": DayTraderCore(),
            # "swing": SwingCore(),
            # "position": PositionCore()
        }

        # Активные стратегии (если не указаны — все)
        if active_strategies is None:
            self.active = list(self.strategies.keys())
        else:
            self.active = [s for s in active_strategies if s in self.strategies]

    def set_mode(self, mode):
        self.mode = mode
        for name in self.strategies:
            self.strategies[name].mode = mode

    def get_signals(self, data):
        """
        Получает рыночные данные, прогоняет через TraderSense,
        затем через все активные стратегии.
        Возвращает список сигналов.
        """
        sense_result = self.trader_sense.analyze(data)
        signals = []

        for name in self.active:
            strategy = self.strategies[name]
            signal = strategy.generate_signal(sense_result, data)
            if signal:
                signal["strategy"] = name
                signals.append(signal)

        return signals, sense_result


# === ТЕСТ ===
if __name__ == "__main__":
    print("=== StrategyPool ТЕСТ ===\n")

    # Тест 1: Lite, InstitutionalCore активен
    sp = StrategyPool(mode="lite")
    print(f"Режим: {sp.mode}")
    print(f"Активные стратегии: {sp.active}")

    data = {
        "asset": "ETH/USDT",
        "price": 4490,
        "level": 4500,
        "volume_current": 500,
        "volume_average": 1000,
        "wick_above_level": 4530,
        "liquidity_above": 2000000,
        "atr": 50
    }

    signals, sense = sp.get_signals(data)
    print(f"\nРыночная фаза: {sense['phase']}")
    print(f"Стоп-ран вероятен: {sense['stop_hunt_likely']}")
    print(f"Найдено сигналов: {len(signals)}")

    for s in signals:
        print(f"  Стратегия: {s['strategy']}")
        print(f"  Сигнал: {s['direction']} {s['asset']} по {s['entry']}")
        print(f"  Стоп: {s['stop_loss']}, Тейк: {s['take_profit']}")

    # Тест 2: нормальный рынок — сигналов нет
    data2 = {
        "asset": "BTC/USDT",
        "price": 60500,
        "level": 60000,
        "volume_current": 2000,
        "volume_average": 1000,
        "wick_above_level": 0,
        "liquidity_above": 0,
        "atr": 100
    }
    signals2, sense2 = sp.get_signals(data2)
    print(f"\nТест 2 (нормальный рынок):")
    print(f"  Фаза: {sense2['phase']}")
    print(f"  Сигналов: {len(signals2)} (ожидается 0)")