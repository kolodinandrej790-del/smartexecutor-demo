# test_keywords.py — проверка keywords.py
from submodules.infosense.keywords import classify_event, get_impact, extract_asset

print("=== Тест classify_event ===")
tests = [
    ("Binance will list XAUT on spot market", "listing"),
    ("OKX will delist XRP trading pair", "delisting"),
    ("DeFi protocol hacked for $50M", "hack"),
    ("SEC files lawsuit against exchange", "regulation"),
    ("Fed raises interest rate by 0.5%", "macro"),
    ("US imposes sanctions on country X", "geopolitics"),
    ("Elon Musk says DOGE is future", "statement"),
    ("Whale transferred 10,000 BTC to Binance", "whale"),
    ("Bitcoin price rises today", "news"),
]

for text, expected in tests:
    result = classify_event(text)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{text[:50]}...' → {result} (ожидалось: {expected})")

print("\n=== Тест get_impact ===")
impact_tests = [
    ("DeFi protocol hacked for $50M", -3),
    ("Binance will list XAUT", +2),
    ("Bitcoin price rises today", 0),
    ("Market crashes as SEC rejects ETF", -3),
]

for text, _ in impact_tests:
    impact = get_impact(text)
    print(f"'{text[:50]}...' → impact = {impact}")

print("\n=== Тест extract_asset ===")
known = ["BTC", "ETH", "XAUT", "PAXG"]
asset_tests = [
    "Binance will list XAUT on spot",
    "BTC price drops 5%",
    "New regulation affects market",
]

for text in asset_tests:
    asset = extract_asset(text, known)
    print(f"'{text[:50]}...' → asset = {asset}")