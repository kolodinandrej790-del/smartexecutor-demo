# test_binance_announcements.py — проверка binance_announcements.py
from submodules.infosense.sources.binance_announcements import (
    fetch_all_announcements,
    clear_cache,
)

print("=== Тест Binance Announcements ===\n")

clear_cache()
events = fetch_all_announcements()

print(f"Всего анонсов: {len(events)}\n")

# Считаем по типам
listings = [e for e in events if e.type == "listing"]
delistings = [e for e in events if e.type == "delisting"]

print(f"Листингов: {len(listings)}")
print(f"Делистингов: {len(delistings)}\n")

# Топ-10
print("=== Топ-10 ===\n")
for i, event in enumerate(events[:10], 1):
    print(f"{i}. [{event.type}] impact={event.impact}")
    print(f"   {event.headline[:90]}")
    if event.asset:
        print(f"   Asset: {event.asset}")
    print()