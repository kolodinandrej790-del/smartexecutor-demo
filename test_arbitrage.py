# test_arbitrage.py — проверка ArbitrageScanner (4 источника)
from submodules.binance_connector import BinanceConnector
from submodules.bybit_connector import BybitConnector
from submodules.okx_connector import OKXConnector
from submodules.kraken_connector import KrakenConnector
from submodules.arbitrage_scanner import ArbitrageScanner

keys = {}
for line in open("keys.txt", encoding="utf-8"):
    if "=" in line:
        k, v = line.split("=", 1)
        keys[k.strip()] = v.strip()

binance = BinanceConnector()
bybit = BybitConnector()
okx = OKXConnector(
    api_key=keys.get("OKX_API_KEY", ""),
    secret_key=keys.get("OKX_SECRET_KEY", ""),
    passphrase=keys.get("OKX_PASSPHRASE", "")
)
kraken = KrakenConnector()

scanner = ArbitrageScanner([binance, bybit, okx, kraken])

# Активы — теперь с Kraken
assets = [
    {
        "name": "XAUT",
        "symbols": {
            "binance": "XAUTUSDT",
            "bybit": "XAUTUSDT",
            "okx": "XAUT-USDT",
            "kraken": "XAUTUSD"
        }
    },
    {
        "name": "BTC",
        "symbols": {
            "binance": "BTCUSDT",
            "bybit": "BTCUSDT",
            "okx": "BTC-USDT",
            "kraken": "XBTUSD"   # ← важно: Kraken использует XBT
        }
    },
    {
        "name": "ETH",
        "symbols": {
            "binance": "ETHUSDT",
            "bybit": "ETHUSDT",
            "okx": "ETH-USDT",
            "kraken": "ETHUSD"
        }
    },
]

print("=== ArbitrageScanner (4 источника) ===\n")
results = scanner.scan_multi(assets, fee_percent=0.1, threshold=0.5)

for r in results:
    print(f"--- {r['asset']} ---")
    if "buy_at" in r:
        print(f"  Купить: {r['buy_at']} за ${r['buy_price']:,.2f}")
        print(f"  Продать: {r['sell_at']} за ${r['sell_price']:,.2f}")
        print(f"  Спред: {r['spread_percent']}%")
        print(f"  Чистая: {r['net_profit_percent']}%")
        print(f"  Сигнал: {'✅ ДА' if r['opportunity'] else '❌ НЕТ'} (порог {r['threshold']}%)")
        # Показываем все цены
        print("  Все цены:")
        for name, p in r['all_prices'].items():
            print(f"    {name}: ${p['price']:,.2f}")
    else:
        print(f"  {r.get('reason', 'нет данных')}")
    print()