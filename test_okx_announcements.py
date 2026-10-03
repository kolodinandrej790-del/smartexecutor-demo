# test_okx_announcements.py — проверка okx_announcements.py
from submodules.infosense.sources.okx_announcements import (
    fetch_all_announcements,
    clear_cache,
)

print("=== Тест OKX Announcements ===\n")

clear_cache()
events = fetch_all_announcements()

print(f"Всего анонсов: {len(events)}\n")

# Топ-10
for i, event in enumerate(events[:10], 1):
    print(f"{i}. [{event.type}] impact={event.impact}")
    print(f"   {event.headline}")
    if event.asset:
        print(f"   Asset: {event.asset}")
    print(f"   URL: {event.url[:80]}")
    print()