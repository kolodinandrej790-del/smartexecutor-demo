# test_infosense.py — проверка фасада InfoSense
from submodules.infosense import InfoSense

print("=== Тест InfoSense (фасад) ===\n")

infosense = InfoSense()
print(f"Модуль: {infosense.name}\n")

# 1. Контекст по рынку
print("=== Контекст по рынку ===")
ctx = infosense.get_market_context()
print(f"Bias: {ctx['bias_info']['bias']}")
print(f"События: {ctx['bias_info']['events_count']}")
print(f"Confidence: {ctx['bias_info']['confidence']}")
print(f"Fear & Greed: {ctx['fear_greed']}")

# 2. Контекст по XAUT
print("\n=== Контекст по XAUT ===")
ctx_xaut = infosense.get_market_context(asset="XAUT")
print(f"Bias: {ctx_xaut['bias_info']['bias']}")
print(f"События: {ctx_xaut['bias_info']['events_count']}")
print(f"Confidence: {ctx_xaut['bias_info']['confidence']}")

# 3. Bias отдельно
print("\n=== Bias по BTC ===")
bias = infosense.get_bias(asset="BTC")
print(f"Bias: {bias['bias']}")
print(f"Confidence: {bias['confidence']}")

# 4. Fear & Greed
print("\n=== Fear & Greed ===")
fg = infosense.get_fear_greed()
print(f"Value: {fg['value']}, Category: {fg['category']}")

print("\n✅ Фасад работает")