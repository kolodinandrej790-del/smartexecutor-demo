# Dispatcher v2.0 — Ядро агента SmartExecutor (+ интеграция с Bybit)

from submodules.risk_manager import RiskManager
from submodules.trade_archive import TradeArchive
from submodules.psychology_guard import PsychologyGuard
from submodules.knowledge_base import KnowledgeBase
from submodules.strategy_pool import StrategyPool
from submodules.bybit_connector import BybitConnector


class Dispatcher:
    def __init__(self, mode="lite", capital=100, risk_percent=2, max_deals=10,
                 active_strategies=None, max_drawdown_percent=20,
                 api_key=None, private_key_path="private_key.pem"):
        self.mode = mode
        self.capital = capital
        self.initial_capital = capital
        self.scalpel_deal_amount = 0
        self.scalpel_profit_buffer = 0

        self.risk_manager = RiskManager(capital, risk_percent, max_deals, max_drawdown_percent)
        self.trade_archive = TradeArchive()
        self.psychology_guard = PsychologyGuard()
        self.knowledge_base = KnowledgeBase()
        self.strategy_pool = StrategyPool(mode, active_strategies)

        # Подключаем биржу, если даны ключи
        if api_key:
            self.connector = BybitConnector(api_key=api_key, private_key_path=private_key_path)
            print("Биржа подключена.")
        else:
            self.connector = None
            print("Биржа НЕ подключена (нет API-ключа).")

        self.session_active = False
        self.open_positions = []

    def start_session(self):
        if self.session_active:
            return "Сессия уже активна."
        warning = self.risk_manager.warning()
        self.session_active = True
        return f"Сессия запущена. Режим: {self.mode}. {warning}"

    def start_scalpel_session(self, deal_amount, max_deals, min_profit_percent=2):
        self.mode = "scalpel"
        self.scalpel_deal_amount = deal_amount
        self.scalpel_profit_buffer = 0
        self.max_deals = max_deals
        self.min_profit_percent = min_profit_percent
        self.deals_done = 0
        self.session_active = True
        return (
            f"Режим SCALPEL активирован.\n"
            f"  Капитал: {self.capital}$\n"
            f"  Сумма сделки: {deal_amount}$ (фикс.)\n"
            f"  Макс. сделок: {max_deals}\n"
            f"  Мин. прибыль: {min_profit_percent}%\n"
            f"  Прибыль не реинвестируется."
        )

    def stop_session(self):
        self.session_active = False
        if self.mode == "scalpel":
            total = self.capital + self.scalpel_profit_buffer
            return f"Сессия SCALPEL остановлена. Сделок: {self.deals_done}. Буфер прибыли: {self.scalpel_profit_buffer:.2f}$. Баланс: {total:.2f}$."
        return f"Сессия остановлена. Открытых позиций: {len(self.open_positions)}"

    def process_market_data(self, data):
        if not self.session_active:
            return {"status": "stopped", "message": "Сессия не активна."}

        if self.psychology_guard.is_blocked():
            return {"status": "blocked", "message": self.psychology_guard.status()}

        if self.mode == "scalpel" and self.deals_done >= self.max_deals:
            return {"status": "blocked", "message": f"Лимит сделок исчерпан: {self.max_deals}"}

        signals, sense = self.strategy_pool.get_signals(data)

        if not signals:
            return {
                "status": "ok",
                "message": f"Сигналов нет. Фаза: {sense['phase']}.",
                "sense": sense
            }

        approved = []
        for signal in signals:
            entry = signal["entry"]
            stop = signal["stop_loss"]
            take_profit = signal["take_profit"]
            asset = signal["asset"]

            if self.mode == "scalpel":
                position_size = self.scalpel_deal_amount / entry if entry > 0 else 0
            else:
                position_size = 0.01

            ok, msg = self.risk_manager.check_deal(entry, stop, position_size)
            if ok:
                approved.append(signal)
                self.risk_manager.deals_opened += 1
                if self.mode == "scalpel":
                    self.deals_done += 1

                # Запись в архив
                self.trade_archive.add(
                    asset=asset,
                    direction=signal["direction"],
                    entry=entry,
                    stop_loss=stop,
                    take_profit=take_profit,
                    strategy=signal.get("strategy", "unknown"),
                    reason=signal.get("reason_text", "")
                )

                # Реальный ордер на биржу
                if self.connector:
                    try:
                        order = self.connector.place_order(
                            symbol=asset,
                            side=signal["direction"],
                            qty=position_size,
                            stop_loss=stop,
                            take_profit=take_profit
                        )
                        signal["order_result"] = order
                    except Exception as e:
                        signal["order_error"] = str(e)

        return {
            "status": "ok",
            "message": f"Одобрено сделок: {len(approved)} из {len(signals)}.",
            "sense": sense,
            "signals": approved
        }

    def feed_trade_result(self, profit_loss):
        self.psychology_guard.feed_result(profit_loss, self.capital)
        if self.mode == "scalpel":
            self.scalpel_profit_buffer += profit_loss
        else:
            self.capital += profit_loss
        ok, msg = self.risk_manager.update_balance(self.capital)
        return {
            "capital": self.capital,
            "buffer": self.scalpel_profit_buffer if self.mode == "scalpel" else 0,
            "psychology": self.psychology_guard.status(),
            "risk": msg
        }

    def explain_deal(self, deal_id, term):
        trade = self.trade_archive.get_by_id(deal_id)
        if not trade:
            return f"Сделка #{deal_id} не найдена."
        return self.knowledge_base.explain_deal(trade, term)

    def explain_term(self, term):
        card = self.knowledge_base.explain_term(term)
        if not card:
            return f"Термин '{term}' не найден."
        return f"{card['term']} ({card['type']}):\n{card['description']}\nСигнал: {card['signal']}"

    def get_balance(self):
        if self.connector:
            return self.connector.get_balance()
        return {"error": "Биржа не подключена"}