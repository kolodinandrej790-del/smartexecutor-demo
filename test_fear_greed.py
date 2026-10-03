# test_fear_greed.py — проверка fear_greed.py
from submodules.infosense.sources.fear_greed import get_fear_greed, clear_cache

print("=== Тест Fear & Greed ===")

# Первый запрос — из сети
clear_cache()
result = get_fear_greed()
print(f"Первый запрос: {result}")

# Второй запрос — из кэша
result2 = get_fear_greed()
print(f"Второй запрос (кэш): {result2}")

# Проверка, что кэш работает
if result and result2 and result["ts"] == result2["ts"]:
    print("✅ Кэш работает")
else:
    print("⚠️ Кэш не сработал или данные не получены")