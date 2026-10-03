# test_rss.py — проверка rss_source.py
from submodules.infosense.sources.rss_source import fetch_all_feeds, clear_cache

print("=== Тест RSS-парсера ===\n")

clear_cache()
events = fetch_all_feeds()

print(f"Всего событий: {len(events)}\n")

# Топ-5 последних
print("=== Топ-5 новостей ===")
for i, event in enumerate(events[:5], 1):
    print(f"{i}. [{event.source}] {event.type} (impact={event.impact})")
    print(f"   {event.headline[:80]}")
    if event.asset:
        print(f"   Asset: {event.asset}")
    print()