# InstitutionalCore v1.1 — Охотник за ликвидностью (+ каскадные ликвидации)

class InstitutionalCore:
    def __init__(self, mode="lite", stop_run_threshold=0.3):
        self.mode = mode
        self.stop_run_threshold = stop_run_threshold

    def generate_signal(self, sense_result, data):
        price = data.get("price", 0)
        level = data.get("level", 0)
        wick = data.get("wick_above_level", 0)
        liquidity = data.get("liquidity_above", 0)
        volume_curr = data.get("volume_current", 0)
        volume_avg = data.get("volume_average", 1)

        # ==========================================
        # СИГНАЛ 1: СТОП-РАН (SELL после ложного пробоя)
        # ==========================================
        if level > 0:
            wick_percent = ((wick - level) / level) * 100 if wick > level else 0
        else:
            wick_percent = 0

        false_breakout = sense_result.get("false_breakout", False)
        volume_weak = sense_result.get("volume_weak", False)

        if false_breakout and volume_weak and wick_percent >= self.stop_run_threshold:
            if self.mode == "pro" and liquidity <= 0:
                pass  # Pro без ликвидности — сигнала нет
            else:
                stop_loss = wick * 1.002
                take_profit = price - (wick - level) * 2
                return {
                    "asset": data.get("asset", "UNKNOWN"),
                    "direction": "SELL",
                    "entry": price,
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(max(take_profit, price * 0.98), 2),
                    "reason_code": "stop_hunt_above_level",
                    "reason_text": f"Стоп-ран над уровнем {level}. Шип {wick_percent:.2f}%. Объём {volume_curr}/{volume_avg}."
                }

        # ==========================================
        # СИГНАЛ 2: КАСКАДНЫЕ ЛИКВИДАЦИИ (BUY после выноса толпы)
        # ==========================================
        # Условия: цена ниже уровня, был шип вниз (вынос лонгов),
        # объём вспыхнул (сработали ликвидации), фаза "storm".
        wick_low = data.get("wick_below_level", 0)
        if wick_low > 0 and price > wick_low:
            # Цена отскочила от низа — возможен разворот
            if sense_result.get("phase") == "storm" and volume_curr > volume_avg * 1.5:
                stop_loss = wick_low * 0.998  # чуть ниже шипа
                take_profit = price + (price - wick_low) * 1.5  # цель вверх
                return {
                    "asset": data.get("asset", "UNKNOWN"),
                    "direction": "BUY",
                    "entry": price,
                    "stop_loss": round(stop_loss, 2),
                    "take_profit": round(take_profit, 2),
                    "reason_code": "liquidation_cascade_reversal",
                    "reason_text": f"Разворот после каскада ликвидаций. Шип вниз до {wick_low}. Объём {volume_curr}/{volume_avg}."
                }

        return None


# === ТЕСТ ===
if __name__ == "__main__":
    from submodules.trader_sense import TraderSense
    ts = TraderSense()

    print("=== InstitutionalCore ТЕСТ (v1.1) ===\n")

    ic = InstitutionalCore(mode="pro", stop_run_threshold=0.2)

    # Тест 1: стоп-ран (старый)
    data1 = {
        "asset": "ETH/USDT", "price": 4490, "level": 4500,
        "volume_current": 500, "volume_average": 1000,
        "wick_above_level": 4530, "liquidity_above": 2000000, "atr": 50,
        "wick_below_level": 0
    }
    s1 = ts.analyze(data1)
    sig1 = ic.generate_signal(s1, data1)
    print(f"Тест 1 (стоп-ран): {sig1['direction'] if sig1 else 'НЕТ'} — {sig1.get('reason_text','') if sig1 else ''}")

    # Тест 2: каскадные ликвидации
    data2 = {
        "asset": "SOL/USDT", "price": 95, "level": 100,
        "volume_current": 50000, "volume_average": 20000,
        "wick_above_level": 0, "liquidity_above": 0, "atr": 10,
        "wick_below_level": 80
    }
    s2 = ts.analyze(data2)
    sig2 = ic.generate_signal(s2, data2)
    print(f"Тест 2 (каскад ликвидаций): {sig2['direction'] if sig2 else 'НЕТ'} — {sig2.get('reason_text','') if sig2 else ''}")
    if sig2:
        print(f"  Вход: {sig2['entry']}, Стоп: {sig2['stop_loss']}, Тейк: {sig2['take_profit']}")

    # Тест 3: нет сигнала
    data3 = {
        "asset": "BTC/USDT", "price": 60500, "level": 60000,
        "volume_current": 1000, "volume_average": 1000,
        "wick_above_level": 0, "liquidity_above": 0, "atr": 100,
        "wick_below_level": 0
    }
    s3 = ts.analyze(data3)
    sig3 = ic.generate_signal(s3, data3)
    print(f"Тест 3 (без сигнала): {'СИГНАЛ (ошибка!)' if sig3 else 'НЕТ (правильно)'}")