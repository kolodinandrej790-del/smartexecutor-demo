# infosense/sources/fear_greed.py — Fear & Greed Index.
# Роль: получать индекс страха и жадности.
# Источник: alternative.me (keyless API).
# Версия 1.1: переключились на alternative.me (CMC больше не работает).

import requests
import time


# Кэш (K-005, TTL 5 минут)
_cache = {
    "value": None,
    "category": None,
    "ts": 0
}
CACHE_TTL_SECONDS = 300  # 5 минут


def _normalize_category(classification: str) -> str:
    """Приводит категорию к нашему формату."""
    if not classification:
        return "neutral"
    return classification.lower().replace(" ", "_")


def get_fear_greed(force_refresh: bool = False):
    """
    Возвращает Fear & Greed Index.
    {'value': int, 'category': str, 'ts': int} или None.
    """
    now = int(time.time())

    # Проверка кэша
    if not force_refresh and _cache["value"] is not None:
        if now - _cache["ts"] < CACHE_TTL_SECONDS:
            return {
                "value": _cache["value"],
                "category": _cache["category"],
                "ts": _cache["ts"]
            }

    # Запрос к alternative.me
    url = "https://api.alternative.me/fng/"
    try:
        resp = requests.get(url, params={"limit": 1}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()

        items = data.get("data", [])
        if not items:
            return None

        first = items[0]
        value = int(first.get("value", 0))
        category = _normalize_category(first.get("value_classification", ""))

        # Обновляем кэш
        _cache["value"] = value
        _cache["category"] = category
        _cache["ts"] = now

        return {
            "value": value,
            "category": category,
            "ts": now
        }

    except Exception:
        return None


def clear_cache():
    """Сбрасывает кэш — для тестов."""
    _cache["value"] = None
    _cache["category"] = None
    _cache["ts"] = 0