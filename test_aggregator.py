# test_aggregator.py — проверка aggregator.py
from submodules.infosense.aggregator import get_market_context, get_all_events

print("=== Тест агрегатора ===\n")

# 1. Все события (RSS: 60 мин, биржи: 24 часа)
events = get_all_events()
print(f"Всего событий: {len(events)}\n")

# Считаем по источникам
by_source = {}
for e in events:
    by_source[e.source] = by_source.get(e.source, 0) + 1
print("По источникам:")
for src, count in sorted(by_source.items()):
    print(f"  {src}: {count}")

# 2. Контекст рынка (без актива)
print("\n=== Контекст рынка ===")
ctx = get_market_context(asset=None)
print(f"Bias: {ctx['bias_info']['bias']}")
print(f"События: {ctx['bias_info']['events_count']}")
print(f"Бычьих: {ctx['bias_info']['bullish_count']}")
print(f"Медвежьих: {ctx['bias_info']['bearish_count']}")
print(f"Нейтральных: {ctx['bias_info']['neutral_count']}")
print(f"Confidence: {ctx['bias_info']['confidence']}")
print(f"Fear & Greed: {ctx['fear_greed']}")

# 3. Контекст по XAUT
print("\n=== Контекст по XAUT ===")
ctx_xaut = get_market_context(asset="XAUT")
print(f"Bias: {ctx_xaut['bias_info']['bias']}")
print(f"События: {ctx_xaut['bias_info']['events_count']}")
print(f"Confidence: {ctx_xaut['bias_info']['confidence']}")

# Топ-10 событий
print("\n=== Топ-10 событий ===")
for i, e in enumerate(ctx['events'][:10], 1):
    asset_str = f" [{e.asset}]" if e.asset else ""
    print(f"{i}. [{e.source}] {e.type}{asset_str} impact={e.impact}")
    print(f"   {e.headline[:80]}")