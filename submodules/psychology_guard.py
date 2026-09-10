# PsychologyGuard v1.0 — Страж дисциплины

class PsychologyGuard:
    def __init__(self, max_consecutive_losses=3, daily_loss_limit_percent=15):
        self.max_consecutive_losses = max_consecutive_losses
        self.daily_loss_limit_percent = daily_loss_limit_percent
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.blocked = False
        self.block_reason = ""

    def feed_result(self, profit_loss, capital):
        """Принимает результат сделки (прибыль/убыток в деньгах) и текущий капитал"""
        if self.blocked:
            return

        self.daily_pnl += profit_loss

        if profit_loss < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        # Проверка серии убытков
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.blocked = True
            self.block_reason = f"Серия из {self.consecutive_losses} убытков подряд"
            return

        # Проверка дневного лимита
        daily_limit = capital * (self.daily_loss_limit_percent / 100)
        if self.daily_pnl < -daily_limit:
            self.blocked = True
            self.block_reason = f"Дневной лимит убытка превышен: {abs(self.daily_pnl):.2f} > {daily_limit:.2f}"
            return

    def is_blocked(self):
        return self.blocked

    def reset(self):
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.blocked = False
        self.block_reason = ""

    def status(self):
        if self.blocked:
            return f"ЗАБЛОКИРОВАН: {self.block_reason}"
        return f"АКТИВЕН: убытков подряд: {self.consecutive_losses}, PnL за день: {self.daily_pnl:.2f}"


# === ТЕСТ ===
if __name__ == "__main__":
    pg = PsychologyGuard(max_consecutive_losses=3, daily_loss_limit_percent=15)
    capital = 100

    print("=== PsychologyGuard ТЕСТ ===")

    # Тест 1: нормальная работа
    pg.feed_result(5, capital)
    print(f"Тест 1 (+5$): {pg.status()}")

    # Тест 2: первый убыток
    pg.feed_result(-10, capital)
    print(f"Тест 2 (-10$): {pg.status()}")

    # Тест 3: второй убыток
    pg.feed_result(-10, capital)
    print(f"Тест 3 (-10$): {pg.status()}")

    # Тест 4: третий убыток — блокировка
    pg.feed_result(-10, capital)
    print(f"Тест 4 (-10$, серия из 3): {pg.status()}")

    # Сброс
    pg.reset()
    print(f"\nСброс: {pg.status()}")

    # Тест 5: превышение дневного лимита
    pg.feed_result(-20, capital)
    print(f"Тест 5 (-20$, лимит 15$): {pg.status()}")