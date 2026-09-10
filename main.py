# main.py v1.2 — Главный скрипт (+ Scalpel + каскадные ликвидации)

from core.dispatcher import Dispatcher


def main():
    print("=" * 50)
    print("SMARTEXECUTOR v1.2 — Агент-Трейдер")
    print("=" * 50)

    print("\nВыберите режим:")
    print("1. Lite (исполнение)")
    print("2. Pro (исполнение + обучение)")
    print("3. Scalpel (личный агент Архитектора)")
    mode_choice = input("> ").strip()

    if mode_choice == "3":
        try:
            capital = float(input("Капитал ($): "))
            deal_amount = float(input("Сумма одной сделки ($): "))
            max_deals = int(input("Максимум сделок: "))
            min_profit = float(input("Мин. прибыль (%): "))
        except ValueError:
            print("Ошибка ввода.")
            return

        agent = Dispatcher(mode="scalpel", capital=capital, risk_percent=100, max_deals=max_deals)
        print(f"\n{agent.start_scalpel_session(deal_amount, max_deals, min_profit)}")
    else:
        mode = "pro" if mode_choice == "2" else "lite"
        try:
            capital = float(input("Капитал ($): "))
            risk = float(input("Риск на капитал (%): "))
            max_deals = int(input("Максимум сделок: "))
        except ValueError:
            print("Ошибка ввода.")
            return

        agent = Dispatcher(mode=mode, capital=capital, risk_percent=risk, max_deals=max_deals)
        print(f"\n{agent.start_session()}")

    print("\nКоманды: exit | stop | term ТЕРМИН | deal НОМЕР")
    print("data ЦЕНА УРОВЕНЬ ОБЪЁМ СР_ОБЪЁМ ШИП_ВВЕРХ ЛИКВ ATR ШИП_ВНИЗ")
    print("result ПРИБЫЛЬ")

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except EOFError:
            break

        if cmd == "exit":
            break
        elif cmd == "stop":
            print(agent.stop_session())
        elif cmd.startswith("term "):
            print(agent.explain_term(cmd[5:]))
        elif cmd.startswith("deal "):
            try:
                print(agent.explain_deal(int(cmd[5:]), "ложный пробой"))
            except ValueError:
                print("Формат: deal НОМЕР")
        elif cmd.startswith("data "):
            parts = cmd[5:].split()
            if len(parts) >= 8:
                try:
                    data = {
                        "asset": "MANUAL", "price": float(parts[0]), "level": float(parts[1]),
                        "volume_current": float(parts[2]), "volume_average": float(parts[3]),
                        "wick_above_level": float(parts[4]), "liquidity_above": float(parts[5]),
                        "atr": float(parts[6]), "wick_below_level": float(parts[7])
                    }
                    r = agent.process_market_data(data)
                    print(f"Статус: {r['status']}, Сообщение: {r['message']}")
                    if r.get("signals"):
                        for s in r["signals"]:
                            print(f"СИГНАЛ: {s['direction']} {s['asset']} по {s['entry']}, стоп: {s['stop_loss']}, тейк: {s['take_profit']}")
                            print(f"  Причина: {s.get('reason_text','')}")
                except ValueError:
                    print("Все параметры data должны быть числами")
            else:
                print("Формат: data ЦЕНА УРОВЕНЬ ОБЪЁМ СР_ОБЪЁМ ШИП_ВВЕРХ ЛИКВ ATR ШИП_ВНИЗ")
        elif cmd.startswith("result "):
            try:
                pl = float(cmd[7:])
                r = agent.feed_trade_result(pl)
                print(f"Баланс: {r['capital']}$, Буфер: {r.get('buffer',0)}$, {r['psychology']}")
            except ValueError:
                print("Формат: result ПРИБЫЛЬ")
        else:
            print("Неизвестная команда")

    print(f"\n{agent.stop_session()}")
    print("Агент остановлен.")


if __name__ == "__main__":
    main()