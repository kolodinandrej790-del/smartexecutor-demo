# RiskManager v1.0 — Математический предохранитель

class RiskManager:
    def __init__(self, capital, risk_percent, max_deals, max_drawdown_percent=20):
        self.capital = capital
        self.risk_percent = risk_percent
        self.max_deals = max_deals
        self.max_drawdown_percent = max_drawdown_percent
        self.peak_balance = capital
        self.daily_loss = 0
        self.deals_opened = 0

    def max_loss_per_deal(self):
        """Максимальный убыток на одну сделку"""
        return self.capital * (self.risk_percent / 100) / self.max_deals

    def check_deal(self, entry, stop_loss, position_size):
        """Проверяет, разрешена ли сделка. Возвращает (разрешено, сообщение)"""
        potential_loss = abs(entry - stop_loss) * position_size
        limit = self.max_loss_per_deal()
        
        if self.deals_opened >= self.max_deals:
            return False, f"ЗАПРЕЩЕНО: исчерпан лимит сделок ({self.max_deals})"
        
        if potential_loss > limit:
            return False, f"ЗАПРЕЩЕНО: убыток {potential_loss:.2f} > лимита {limit:.2f}"
        
        return True, f"РАЗРЕШЕНО: убыток {potential_loss:.2f} в лимите {limit:.2f}"

    def update_balance(self, new_balance):
        """Обновляет баланс и проверяет просадку"""
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
        
        drawdown = (self.peak_balance - new_balance) / self.peak_balance * 100
        
        if drawdown >= self.max_drawdown_percent:
            return False, f"СТОП: просадка {drawdown:.1f}% достигла лимита {self.max_drawdown_percent}%"
        
        self.capital = new_balance
        return True, f"ОК: просадка {drawdown:.1f}%"

    def warning(self):
        """Предупреждение о высоком риске"""
        if self.risk_percent > 10:
            return "КРАСНЫЙ: риск более 10%!"
        elif self.risk_percent > 5:
            return "ЖЁЛТЫЙ: риск выше 5%"
        return "ОК"


# === ТЕСТ ===
if __name__ == "__main__":
    rm = RiskManager(capital=100, risk_percent=10, max_deals=10, max_drawdown_percent=20)
    
    print("=== RiskManager ТЕСТ ===")
    print(f"Капитал: {rm.capital}$")
    print(f"Риск на сделку: {rm.risk_percent}%")
    print(f"Макс. убыток на сделку: {rm.max_loss_per_deal():.2f}$")
    print(f"Предупреждение: {rm.warning()}")
    
    # Тест 1: безопасная сделка
    ok, msg = rm.check_deal(entry=4500, stop_loss=4490, position_size=0.5)
    print(f"\nТест 1 (безопасно): {msg}")
    
    # Тест 2: слишком широкий стоп
    ok, msg = rm.check_deal(entry=4500, stop_loss=4000, position_size=0.5)
    print(f"Тест 2 (широкий стоп): {msg}")
    
    # Тест 3: просадка
    ok, msg = rm.update_balance(75)
    print(f"Тест 3 (просадка до 75$): {msg}")
    
    # Тест 4: критическая просадка
    ok, msg = rm.update_balance(50)
    print(f"Тест 4 (просадка до 50$): {msg}")