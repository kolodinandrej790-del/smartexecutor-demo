# TraderSense v1.0 — Интерпретатор рыночных данных

class TraderSense:
    def __init__(self):
        self.current_phase = "neutral"  # neutral, trending, volatile, storm

    def analyze(self, data):
        """
        Получает пакет от внешней Аналитики:
        {
            "price": float,
            "level": float (ближайший сильный уровень),
            "volume_current": float,
            "volume_average": float,
            "wick_above_level": float (макс. цена над уровнем),
            "liquidity_above": float (объём ликвидности над уровнем, опционально),
            "atr": float (средний истинный диапазон)
        }
        Возвращает словарь с интерпретацией.
        """
        result = {
            "phase": self._detect_phase(data),
            "false_breakout": False,
            "volume_weak": False,
            "stop_hunt_likely": False,
            "message": ""
        }

        price = data.get("price", 0)
        level = data.get("level", 0)
        vol_curr = data.get("volume_current", 0)
        vol_avg = data.get("volume_average", 1)  # избегаем деления на 0
        wick = data.get("wick_above_level", 0)
        liquidity = data.get("liquidity_above", 0)

        # 1. Проверка ложного пробоя
        if wick > 0 and price < level:
            result["false_breakout"] = True
            result["message"] += "Обнаружен ложный пробой уровня. "

        # 2. Проверка объёма
        if vol_curr < vol_avg * 0.7:
            result["volume_weak"] = True
            result["message"] += "Объём ниже среднего — пробой слабый. "

        # 3. Вероятность стоп-рана
        if result["false_breakout"] and result["volume_weak"]:
            result["stop_hunt_likely"] = True
            result["message"] += "ВЫСОКАЯ ВЕРОЯТНОСТЬ СТОП-РАНА. "

        # 4. Учёт ликвидности (Pro-режим)
        if liquidity > 0 and result["stop_hunt_likely"]:
            result["message"] += f"Ликвидность над уровнем: {liquidity:.0f}$. "

        # 5. Фаза рынка
        result["phase"] = self._detect_phase(data)
        self.current_phase = result["phase"]

        return result

    def _detect_phase(self, data):
        """Определяет рыночную фазу по ATR"""
        atr = data.get("atr", 0)
        price = data.get("price", 1)
        atr_percent = (atr / price) * 100 if price > 0 else 0

        if atr_percent > 5:
            return "storm"
        elif atr_percent > 2:
            return "volatile"
        elif atr_percent > 0.5:
            return "trending"
        else:
            return "neutral"

    def get_phase(self):
        return self.current_phase


# === ТЕСТ ===
if __name__ == "__main__":
    ts = TraderSense()

    print("=== TraderSense ТЕСТ ===\n")

    # Тест 1: стоп-ран
    data1 = {
        "price": 4490,
        "level": 4500,
        "volume_current": 500,
        "volume_average": 1000,
        "wick_above_level": 4520,
        "liquidity_above": 2000000,
        "atr": 50
    }
    result1 = ts.analyze(data1)
    print(f"Тест 1 (стоп-ран):")
    print(f"  Фаза: {result1['phase']}")
    print(f"  Ложный пробой: {result1['false_breakout']}")
    print(f"  Объём слабый: {result1['volume_weak']}")
    print(f"  Стоп-ран вероятен: {result1['stop_hunt_likely']}")
    print(f"  Сообщение: {result1['message']}")

    # Тест 2: нормальный рынок
    data2 = {
        "price": 4550,
        "level": 4500,
        "volume_current": 2000,
        "volume_average": 1000,
        "wick_above_level": 0,
        "liquidity_above": 0,
        "atr": 20
    }
    result2 = ts.analyze(data2)
    print(f"\nТест 2 (нормальный рынок):")
    print(f"  Фаза: {result2['phase']}")
    print(f"  Стоп-ран вероятен: {result2['stop_hunt_likely']}")
    print(f"  Сообщение: '{result2['message']}'")

    # Тест 3: шторм
    data3 = {
        "price": 4500,
        "level": 4500,
        "volume_current": 5000,
        "volume_average": 1000,
        "wick_above_level": 0,
        "liquidity_above": 0,
        "atr": 300
    }
    result3 = ts.analyze(data3)
    print(f"\nТест 3 (шторм):")
    print(f"  Фаза: {result3['phase']}")