# Источники

Справочник по источникам данных для InfoSense.

---

## 1. Что такое источник

**Источник** — канал, откуда агент берёт **данные** о рынке.

**Три уровня:**
- **Primary** (первичные) — факты от бирж, on-chain, метрики.
- **Secondary** (вторичные) — СМИ, аналитика.
- **Контекст** — макро, геополитика.

**Правило (R-039):**
- Primary — **драйверы**.
- Secondary — **контекст**.
- Событие + реакция = **решающий вес**.

---

## 2. Биржевые анонсы (primary)

**Что:** официальные объявления бирж.
- Листинги.
- Делистинги.
- Технические работы.
- Изменения правил.

### Источники
- **OKX Announcements:** `okx.com/help/section/announcements`
- **Binance Announcements:** `binance.com/en/support/announcement`
- **Bybit Announcements:** `bybit.com/en/help-center/announcement`

### Формат
- JSON (через API).
- HTML / RSS (если API нет).

### Вес
- 🔴 **Критично.** Это **факты**.

### Что даёт
- Тип: `listing`, `delisting`.
- Влияние: `+2` до `+3` / `-2` до `-3`.

---

## 3. RSS (secondary)

**Что:** новостные фиды от СМИ.

### Источники
- **CoinDesk:** `coindesk.com/arc/outboundfeeds/rss/`
- **Cointelegraph:** `cointelegraph.com/rss`
- **The Block:** `theblock.co/rss.xml`
- **Bitcoin Magazine:** `bitcoinmagazine.com/feed`

### Формат
- RSS (XML).
- Парсится через `feedparser` (Python).

### Вес
- 🟡 **Средний.** Это **пересказ**, не факт.

### Что даёт
- Тип: `regulation`, `hack`, `geopolitics`, `statement`.
- Влияние: `-2` до `+2`.

### Ограничение
- **Третье лицо.** Может исказить.
- Использовать **для контекста**, не для драйвера.

---

## 4. CoinMarketCap API

**Что:** агрегатор данных о крипте.

### Тарифы
- **Basic:** 15 000 кредитов/мес.
- **Startup:** 450 000 кредитов/мес (активирован по хакатону).
- **Growth+:** аналитические endpoints.

### Что даёт
- Цены по 483 парам XAUT.
- RWA-данные (эмитенты, токены).
- Метаданные монет.
- Листинги (топ-N).
- Глобальные метрики.

### Endpoints
- `/v3/cryptocurrency/quotes/latest` — цены.
- `/v3/cryptocurrency/listings/latest` — топ.
- `/v5/real-world-assets/issuers/list` — RWA.
- `/v5/real-world-assets/issuers?issuer_id=...` — токены эмитента.

### Вес
- 🟡 **Средний.** Агрегатор.

### Особенности
- `data` — **список или словарь** (различается).
- `quote` — **список** (даже для одной валюты).
- `symbol` не уникален — фильтровать по `slug` или `id`.

### Недоступно
- ❌ `market-pairs` — только на Growth.

---

## 5. Fear & Greed Index

**Что:** индекс настроения рынка. 0–100.

### Источник
- CoinMarketCap (keyless).
- Alternative.me (популярный).

### Что показывает
- 0–25 — extreme fear (паника).
- 25–45 — fear.
- 45–55 — нейтрально.
- 55–75 — greed.
- 75–100 — extreme greed.

### Вес
- 🟢 **Полезно** для контекста.

### Что даёт
- Тип: `macro`.
- Влияние: зависит от значения.

---

## 6. On-chain (планируется)

**Что:** данные из блокчейна.
- Крупные переводы (whale).
- Движение на биржи / с бирж.
- Киты.

### Источники (возможные)
- Whale Alert API.
- Glassnode.
- Nansen.

### Вес
- 🟡 **Средний.**

### Статус
- ⏳ **Планируется** (после W-01).

---

## 7. X / Twitter (планируется)

**Что:** посты в X.
- Официальные аккаунты (Binance, OKX, SEC).
- Авторитеты (Маск, Сэйлор).

### Вес
- 🟡 **Средний.**

### Проблема
- 💰 **Платно** ($100+ / мес).
- **Отложено.**

### Статус
- ⏳ **Backlog.**

---

## 8. Приоритеты

| Уровень | Источник | Вес | Статус |
|---------|----------|-----|--------|
| **1** | Биржевые анонсы | 🔴 Критично | Реализуем |
| **1** | Цены (публичные API) | 🔴 Критично | Работает |
| **2** | CoinMarketCap API | 🟡 Средний | Работает |
| **2** | RSS (СМИ) | 🟡 Средний | Реализуем |
| **3** | Fear & Greed | 🟢 Полезно | Реализуем |
| **4** | On-chain | 🟢 Полезно | Backlog |
| **4** | X / Twitter | 🟢 Полезно | Backlog |

---

## 9. Что используем мы

### Сейчас (W-01)
- ✅ Биржевые анонсы (OKX, Binance).
- ✅ Публичные API (Binance, Bybit, OKX, Kraken).
- ✅ CoinMarketCap (цены, RWA).

### Скоро (W-01)
- ⏳ RSS (CoinDesk, Cointelegraph, The Block).
- ⏳ Fear & Greed.

### Позже (W-02+)
- ⏳ On-chain.
- ⏳ X / Twitter.

---

## 10. Формат данных

**Все источники** — в единый `Event`:
```python
@dataclass
class Event:
    ts: int
    source: str            # "okx_announcements", "coindesk", ...
    source_type: str       # primary / secondary
    type: str              # listing / delisting / regulation / hack / macro / whale / geopolitics / statement / manipulation
    asset: Optional[str]
    impact: int            # -3..+3
    market_reaction: Optional[dict]
    confidence: str
    headline: str
    url: str
    raw: dict

11. Таблица
Источник	Тип	Вес	Формат	Статус
OKX Announcements	primary	🔴	JSON	Реализуем
Binance Announcements	primary	🔴	JSON	Реализуем
Public APIs (prices)	primary	🔴	JSON	Работает
CMC API	secondary	🟡	JSON	Работает
RSS (CoinDesk)	secondary	🟡	XML	Реализуем
RSS (Cointelegraph)	secondary	🟡	XML	Реализуем
RSS (The Block)	secondary	🟡	XML	Реализуем
Fear & Greed	secondary	🟢	JSON	Реализуем
On-chain	primary	🟡	JSON	Backlog
X / Twitter	secondary	🟡	JSON	Backlog

12. Что важно для архитектуры
InfoSense — собирает из всех источников.

Каждый источник — отдельный парсер (sources/).

Вес — учитывается в impact.

Primary > secondary.

Событие + реакция = решающий вес (R-039).

13. Требует проверки
⚠️ Точные URL анонсов OKX / Binance.

⚠️ API для Fear & Greed.

⚠️ Rate limits для каждого источника.

⚠️ Языки источников (русский / английский).

Конец файла.