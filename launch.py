# launch.py v2.0 — Автономный агент SmartExecutor

from core.dispatcher import Dispatcher
import time

# ====================== НАСТРОЙКИ ======================
API_KEY = "Sk8joaAVkOBay1SA2h"
MODE = "pro"
CAPITAL = 100
RISK_PERCENT = 10
MAX_DEALS = 10
SYMBOLS = ["ETHUSDT", "BTCUSDT"]  # активы для отслеживания
LEVELS = {"ETHUSDT": 4500, "BTCUSDT": 60000}  # ключевые уровни
CHECK_INTERVAL = 60  # секунд между проверками
# =======================================================

agent = Dispatcher(
    mode=MODE, capital=CAPITAL, risk_percent=RISK_PERCENT,
    max_deals=MAX_DEALS, api_key=API_KEY
)

print("=" * 50)
print("SMARTEXECUTOR v2.0 — АВТОНОМНЫЙ РЕЖИМ")
print("=" * 50)
print(agent.start_session())
print(f"Отслеживаю: {SYMBOLS}")
print(f"Интервал проверки: {CHECK_INTERVAL} сек.")
print("Нажми Ctrl+C для остановки")

try:
    while True:
        for symbol in SYMBOLS:
            level = LEVELS.get(symbol, 0)
            
            # Собираем рыночные данные
            data = agent.connector.gather_market_data(symbol, level)
            if data is None:
                print(f"[{symbol}] Ошибка получения данных, пропускаю...")
                continue
            
            # Обрабатываем через диспетчер
            result = agent.process_market_data(data)
            
            if result.get("signals"):
                print(f"\n{'='*40}")
                print(f"[{symbol}] СИГНАЛ НАЙДЕН!")
                for s in result["signals"]:
                    print(f"  {s['direction']} по {s['entry']:.2f}")
                    print(f"  Стоп: {s['stop_loss']:.2f}, Тейк: {s['take_profit']:.2f}")
                    if "order_result" in s:
                        print(f"  Ордер: {s['order_result'].get('retMsg', '?')}")
                print(f"{'='*40}\n")
            else:
                phase = result.get("sense", {}).get("phase", "?")
                msg = result.get("message", "")
                print(f"[{symbol}] Цена: {data['price']:.2f} | Фаза: {phase} | {msg}")
        
        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\nОстановка по команде...")

print(agent.stop_session())
print("Агент остановлен.")