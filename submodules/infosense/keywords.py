# infosense/keywords.py — Словари ключевых слов для классификации событий.
# Роль: определять тип события и влияние по тексту.
# Версия 1.0.

from typing import Optional, Tuple


# ========== ТИПЫ СОБЫТИЙ ==========

LISTING_KEYWORDS = [
    "will list", "will be listed", "listing", "lists", "added to",
    "new listing", "spot listing", "perpetual listing",
    "will launch", "launches trading", "now available",
]

DELISTING_KEYWORDS = [
    "will delist", "delisting", "delists", "removed from",
    "will be removed", "cease trading", "suspension",
    "will suspend", "no longer supported",
]

HACK_KEYWORDS = [
    "hack", "hacked", "exploit", "exploited", "breach",
    "stolen", "drained", "vulnerability", "attack",
    "compromised", "rug pull", "rugpull",
]

REGULATION_KEYWORDS = [
    "sec", "cftc", "regulation", "regulatory", "lawsuit",
    "charges", "fine", "settlement", "compliance",
    "ban", "banned", "illegal", "court", "judge",
    "clarity act", "mica", "etf approval", "etf rejection",
]

MACRO_KEYWORDS = [
    "fed", "federal reserve", "interest rate", "rate hike",
    "rate cut", "inflation", "cpi", "jobs report",
    "gdp", "recession", "treasury", "bond yield",
    "fomc", "powell", "monetary policy",
]

GEOPOLITICS_KEYWORDS = [
    "sanctions", "sanction", "war", "conflict", "military",
    "invasion", "nato", "brics", "geopolitical",
    "tension", "crisis", "embargo",
]

STATEMENT_KEYWORDS = [
    "says", "said", "tweeted", "announced", "claims",
    "predicts", "expects", "believes", "warns",
    "musk", "saylor", "trump", "buffett",
]

WHALE_KEYWORDS = [
    "whale", "large transfer", "transferred", "moved",
    "million btc", "million eth", "wallet",
]


# ========== ОЦЕНКА ВЛИЯНИЯ ==========

BULLISH_WORDS = [
    "surge", "soar", "rally", "gain", "rise", "up",
    "bullish", "approval", "approved", "partnership",
    "adoption", "breakthrough", "record high", "all-time high",
]

BEARISH_WORDS = [
    "crash", "plunge", "dump", "fall", "drop", "down",
    "bearish", "rejection", "rejected", "lawsuit",
    "hack", "stolen", "ban", "banned", "probe",
    "investigation", "warning",
]


# ========== ФУНКЦИИ ==========

def classify_event(text: str) -> str:
    """
    Определяет тип события по тексту.
    Возвращает: listing / delisting / hack / regulation / macro / geopolitics / statement / whale / news.
    """
    if not text:
        return "news"

    text_lower = text.lower()

    # Проверяем в порядке приоритета (критичные — первыми)
    if any(kw in text_lower for kw in DELISTING_KEYWORDS):
        return "delisting"
    if any(kw in text_lower for kw in LISTING_KEYWORDS):
        return "listing"
    if any(kw in text_lower for kw in HACK_KEYWORDS):
        return "hack"
    if any(kw in text_lower for kw in REGULATION_KEYWORDS):
        return "regulation"
    if any(kw in text_lower for kw in GEOPOLITICS_KEYWORDS):
        return "geopolitics"
    if any(kw in text_lower for kw in MACRO_KEYWORDS):
        return "macro"
    if any(kw in text_lower for kw in WHALE_KEYWORDS):
        return "whale"
    if any(kw in text_lower for kw in STATEMENT_KEYWORDS):
        return "statement"

    return "news"


def get_impact(text: str) -> int:
    """
    Оценивает влияние события по тексту.
    Возвращает: -3..+3.
    """
    if not text:
        return 0

    text_lower = text.lower()

    bullish_count = sum(1 for w in BULLISH_WORDS if w in text_lower)
    bearish_count = sum(1 for w in BEARISH_WORDS if w in text_lower)

    # Тип события может усилить влияние
    event_type = classify_event(text)
    if event_type == "hack":
        return -3
    if event_type == "delisting":
        return -3
    if event_type == "listing":
        return +2

    # По словам
    if bearish_count > bullish_count:
        return max(-3, -bearish_count)
    if bullish_count > bearish_count:
        return min(+3, bullish_count)
    return 0


def extract_asset(text: str, known_assets: list) -> Optional[str]:
    """
    Извлекает упоминание актива из текста.
    known_assets: список известных тикеров, например ["BTC", "ETH", "XAUT"].
    Возвращает тикер или None.
    """
    if not text:
        return None

    text_upper = text.upper()
    for asset in known_assets:
        if asset.upper() in text_upper:
            return asset
    return None