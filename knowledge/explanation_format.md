# Формат объяснений

Справочник по формату объяснений решений агента.

---

## 1. Что такое explanation

**Explanation** — **текстовое описание** решения агента.

**Не просто:**
- «Купил XAUT».

**А:**
- «Купил XAUT, потому что:
  - обнаружен ложный пробой над уровнем 4300;
  - фитиль 4320 (0.47%);
  - объём ниже среднего (500/1000);
  - TraderSense: stop_hunt_likely=true;
  - confidence HIGH (TrendAnalyzer и TraderSense согласны);
  - профиль spot_long активен;
  - новостей нет, макро спокойное».

**Ключевое:** explanation — **почему**, а не только **что**.

---

## 2. Отличие от логов

| Лог | Explanation |
|-----|-------------|
| Для **отладки** | Для **понимания** |
| Технические детали | Смысл решения |
| Программисту | Пользователю |
| Может быть шумным | Только по делу |
| В `.log` файлах | В `trade_log.md`, `lessons.json` |

**Лог:** `[2026-09-27 14:30] TradeArchive.add: trade_id=42`.
**Explanation:** «Открыта сделка XAUT BUY. Причина: stop_hunt_likely=true. Confidence HIGH».

---

## 3. Поля

**Структура explanation:**

```python
{
  "trade_id": 42,
  "ts": 1734567890,
  "asset": "XAUT",
  "action": "BUY",
  "profile": "spot_long",
  
  "reason_code": "stop_hunt_likely",
  "reason_text": "Обнаружен ложный пробой над уровнем 4300. Фитиль 4320 (0.47%).",
  
  "explanation": "Полное описание: ...",
  
  "context": {
    "trend": "up",
    "volatility_level": "trending",
    "session": "europe",
    "news": "нет значимых событий",
    "geopolitics": "спокойно",
    "xaut_price": 4300,
    "btc_price": 84000
  },
  
  "confidence": "HIGH",
  "confidence_reason": "TrendAnalyzer и TraderSense согласны",
  
  "modules_involved": [
    "LevelBuilder",
    "TraderSense",
    "TrendAnalyzer",
    "ContextGate",
    "RiskManager"
  ],
  
  "decision_chain": [
    "LevelBuilder: подготовил данные",
    "TraderSense: stop_hunt_likely=true",
    "TrendAnalyzer: trend=up",
    "ContextGate: PASS (все согласны)",
    "RiskManager: 2% риск OK",
    "OKXConnector: order sent"
  ]
}

4. Примеры
Пример 1. Успешная сделка BUY
{
  "trade_id": 42,
  "asset": "XAUT",
  "action": "BUY",
  "profile": "spot_long",
  "reason_code": "stop_hunt_likely",
  "explanation": "Вошли в BUY по паттерну стоп-ран. Цена сделала ложный пробой над уровнем 4300 (фитиль 4320, 0.47%), вернулась под уровень. Объём ниже среднего (500/1000). TraderSense подтверждает stop_hunt_likely=true. TrendAnalyzer показывает тренд вверх. Confidence HIGH.",
  "confidence": "HIGH"
}

Пример 2. Сделка НЕ открыта

{
  "trade_id": null,
  "asset": "ETH",
  "action": "BLOCKED",
  "profile": "spot_long",
  "reason_code": "negative_news",
  "explanation": "Сигнал BUY по стоп-рану, но ContextGate заблокировал. Причина: только что вышла негативная новость про ETH (регуляторное расследование). Риск слишком высокий.",
  "context": {
    "news": "SEC расследует Ethereum Foundation",
    "trend": "down",
    "volatility_level": "volatile"
  },
  "confidence": "LOW"
}

Пример 3. Арбитраж — сигнал
{
  "trade_id": 43,
  "asset": "XAUT",
  "action": "ARBITRAGE",
  "profile": "arbitrage_cross",
  "reason_code": "cross_exchange_spread",
  "explanation": "Обнаружено расхождение XAUT между Binance ($4283.63) и OKX ($4284.60) = 0.023%. После вычета комиссий 0.2% — чистая -0.177%. Сигнал НЕ подтверждён (порог 0.5%).",
  "confidence": "HIGH"
}

5. Где хранится
TradeArchive
Каждая сделка → explanation в trades.json.

Поле explanation.

lessons.json
Уроки из сделок.

С объяснениями.

MarketCaseArchive
Кейсы рынка.

С объяснениями.

Формат: .md + index.jsonl.

confidence.jsonl (Архивариус)
Confidence-записи.

С полем summary.

trade_log.md
Человекочитаемый лог.

Формат: markdown.

6. Как читается
Пользователем
Открывает trade_log.md → видит объяснение простым языком.

Или команда агенту: «объясни сделку #42» → ответ.

Агентом (для обучения)
TradeAnalyzer читает explanation.

Сравнивает с результатом.

Делает вывод.

Supervisor (для аудита)
Смотрит, где explanation не совпадает с результатом.

Помечает для разбора.

7. Что делаем мы
При открытии сделки
Формируем explanation из:

сигнала стратегии;

контекста (InfoSense, TrendAnalyzer);

confidence (Methodist);

решения ContextGate.

При закрытии
Обновляем explanation с результатом.

Пишем в lessons.json.

При блокировке
Пишем explanation с причиной блокировки.

Полезно для разбора: «почему не вошли».

Позже
Команда «объясни» в агенте.

Автоматические отчёты.

8. Таблица — что даёт explanation
Кому	Что даёт
Пользователю	Понимание решений
Агенту	Обучение на объяснениях
Supervisor	Аудит
TradeAnalyzer	Разбор сделок
MarketCaseArchive	Хранение кейсов
Разработчику	Отладка
9. Что важно для архитектуры
K-026 — каждое решение с объяснением.

Explanation ≠ Log.

Формат — единый (dataclass в contracts.py).

Хранение — TradeArchive + lessons.json + MarketCaseArchive.

Это — наша уникальность. 

10. Требует проверки
⚠️ Точный формат dataclass Explanation.

⚠️ Как генерировать explanation автоматически.

⚠️ Как читать объяснения пользователю (CLI / API).

Конец файла.