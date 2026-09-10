# launch_okx.py — Боевой запуск SmartExecutor на OKX (спот ETH-USDT)
# Версия: 3 уровня + BUY/SELL + проверка ордера + библиотека уроков

from core.dispatcher import Dispatcher
from submodules.okx_connector import OKXConnector
from submodules.position_manager import PositionManager
import time

# ====================== БОЕВЫЕ НАСТРОЙКИ ======================
SYMBOL = "ETH-USDT"
LEVELS = [2500, 2480, 2400]
DEAL_AMOUNT = 5
MAX_DEALS = 3
TAKE_PROFIT_PERCENT = 2.0
STOP_LOSS_PERCENT = 1.5
CHECK_INTERVAL = 30
DAILY_LOSS_LIMIT = 5
INITIAL_CAPITAL = 20
# ==============================================================

with open("keys.txt", "r") as f:
    lines = f.readlines()

keys = {}
for line in lines:
    line = line.strip()
    if "=" in line:
        k, v = line.split("=", 1)
        keys[k.strip()] = v.strip()

connector = OKXConnector(
    api_key=keys.get("OKX_API_KEY", ""),
    secret_key=keys.get("OKX_SECRET_KEY", ""),
    passphrase=keys.get("OKX_PASSPHRASE", "")
)

agent = Dispatcher(mode="pro", capital=INITIAL_CAPITAL, risk_percent=20, max_deals=MAX_DEALS)
agent.connector = connector
agent.session_active = True
agent.deals_done = 0
agent.max_deals = MAX_DEALS
agent.current_balance = INITIAL_CAPITAL

open_position = None

print("=" * 50)
print("SMARTEXECUTOR v2.0 — OKX SPOT [BUY/SELL]")
print("=" * 50)
print(f"Актив: {SYMBOL}")
print(f"Уровни: {LEVELS}")
print(f"Сумма сделки: ${DEAL_AMOUNT}")
print(f"Максимум сделок: {MAX_DEALS}")
print(f"Тейк-профит: +{TAKE_PROFIT_PERCENT}%")
print(f"Стоп-лосс: -{STOP_LOSS_PERCENT}%")
print(f"Дневной лимит убытка: {DAILY_LOSS_LIMIT}%")
print(f"Интервал: {CHECK_INTERVAL} сек.")
print("Нажми Ctrl+C для остановки")
print("=" * 50)

def check_signal(data):
    from submodules.trader_sense import TraderSense
    from submodules.institutional_core import InstitutionalCore

    ts = TraderSense()
    ic = InstitutionalCore(mode="lite")

    sense = ts.analyze(data)
    signal = ic.generate_signal(sense, data)
    return signal, sense

def get_best_data():
    best = None
    for lvl in LEVELS:
        d = connector.gather_market_data(SYMBOL, lvl)
        if d is not None:
            if best is None:
                best = d
            else:
                dist_new = abs(d["price"] - lvl)
                dist_best = abs(best["price"] - best["level"])
                if dist_new < dist_best:
                    best = d
    return best

try:
    while True:
        # === 1. Сопровождение позиции ===
        if open_position is not None and not open_position.closed:
            status = open_position.check()
            print(open_position.status_text())

            if open_position.closed:
                print(f"Позиция закрыта: {status} по {open_position.close_price:.2f}")
                result = open_position.close_position()
                print(f"Ордер закрытия: {result.get('msg', result)}")

                if status == "CLOSED_TP":
                    profit = DEAL_AMOUNT * TAKE_PROFIT_PERCENT / 100
                else:
                    profit = -DEAL_AMOUNT * STOP_LOSS_PERCENT / 100

                agent.current_balance += profit
                print(f"Прибыль/убыток: {profit:.2f}$ | Баланс: {agent.current_balance:.2f}$")

                connector.log_trade(
                    symbol=SYMBOL,
                    side=open_position.direction,
                    entry=open_position.entry_price,
                    stop=open_position.stop_loss,
                    take=open_position.take_profit,
                    status=status
                )

                lesson_reason = "TP" if status == "CLOSED_TP" else "SL"
                connector.log_lesson(
                    symbol=SYMBOL,
                    side=open_position.direction,
                    entry=open_position.entry_price,
                    exit_price=open_position.close_price,
                    profit=profit,
                    reason=lesson_reason
                )

                open_position = None

            time.sleep(CHECK_INTERVAL)
            continue

        # === 2. Дневной лимит убытка ===
        daily_loss = INITIAL_CAPITAL - agent.current_balance
        if daily_loss >= INITIAL_CAPITAL * DAILY_LOSS_LIMIT / 100:
            print(f"\nДНЕВНОЙ ЛИМИТ УБЫТКА ДОСТИГНУТ: {daily_loss:.2f}$")
            print("Агент останавливается.")
            break

        # === 3. Лимит сделок ===
        if agent.deals_done >= MAX_DEALS:
            print(f"\nЛимит сделок исчерпан: {MAX_DEALS}. Агент ждёт решения.")
            time.sleep(60)
            continue

        # === 4. Получение данных ===
        data = get_best_data()
        if data is None:
            print(f"[{SYMBOL}] Ошибка данных")
            time.sleep(CHECK_INTERVAL)
            continue

        # === 5. Проверка сигнала ===
        signal, sense = check_signal(data)

        if signal:
            price = data.get("price", 0)
            qty = DEAL_AMOUNT / price if price > 0 else 0

            take_profit = price * (1 + TAKE_PROFIT_PERCENT / 100)
            stop_loss = price * (1 - STOP_LOSS_PERCENT / 100)

            if signal["direction"] == "SELL":
                take_profit = price * (1 - TAKE_PROFIT_PERCENT / 100)
                stop_loss = price * (1 + STOP_LOSS_PERCENT / 100)

            print(f"\n{'='*40}")
            print(f"СИГНАЛ: {signal['direction']} {SYMBOL}")
            print(f"Цена: {price:.2f}")
            print(f"Стоп: {stop_loss:.2f}")
            print(f"Тейк: {take_profit:.2f}")
            print(f"Причина: {signal.get('reason_text','')}")
            print(f"Количество: {qty:.6f}")
            print(f"{'='*40}\n")

            try:
                order = connector.place_order(
                    symbol=SYMBOL,
                    side="buy" if signal["direction"] == "BUY" else "sell",
                    qty=round(qty, 6)
                )

                if order.get("code") == "0":
                    print(f"Ордер принят: {order.get('msg','')}")

                    open_position = PositionManager(
                        connector=connector,
                        symbol=SYMBOL,
                        qty=qty,
                        entry_price=price,
                        take_profit=take_profit,
                        stop_loss=stop_loss,
                        direction=signal["direction"]
                    )

                    agent.deals_done += 1
                    print(f"Сделок использовано: {agent.deals_done} из {MAX_DEALS}")
                    print(f"Позиция открыта: {open_position.status_text()}")
                else:
                    print(f"Ордер ОТКЛОНЁН: {order.get('msg', order)}")
                    print("Сделка не засчитана.")

            except Exception as e:
                print(f"Ошибка ордера: {e}")
        else:
            phase = sense.get("phase", "?")
            price = data.get("price", 0)
            level = data.get("level", 0)
            print(f"[{SYMBOL}] Цена: {price:.2f} | Уровень: {level} | Фаза: {phase} | Баланс: {agent.current_balance:.2f}$ | Сделок: {agent.deals_done}/{MAX_DEALS}")

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\nОстановка по команде...")

print(f"\nИтог: использовано сделок {agent.deals_done} из {MAX_DEALS}")
print(f"Баланс: {agent.current_balance:.2f}$")
print("Агент остановлен.")