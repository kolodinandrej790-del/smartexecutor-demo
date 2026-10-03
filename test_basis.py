# test_basis.py — проверка BasisScanner
from submodules.bybit_connector import BybitConnector
from submodules.binance_connector import BinanceConnector
from submodules.basis_scanner import BasisScanner

bybit = BybitConnector()
binance = BinanceConnector()

scanner = BasisScanner([bybit, binance])

print("=== BasisScanner: spot vs linear ===\n")

# Bybit имеет и spot, и linear
assets = [
    {"name": "XAUT", "symbol": "XAUTUSDT"},
    {"name": "BTC", "symbol": "BTCUSDT"},
    {"name": "ETH", "symbol": "ETHUSDT"},
    {"name": "PAXG", "symbol": "PAXGUSDT"},
]

for asset in assets:
    results = scanner.scan(asset["name"], asset["symbol"], threshold=0.5)
    print(f"--- {asset['name']} ---")
    if results:
        for r in results:
            print(f"  Биржа: {r['exchange']}")
            print(f"  Купить: {r['buy_at']} за ${r['buy_price']:,.2f}")
            print(f"  Продать: {r['sell_at']} за ${r['sell_price']:,.2f}")
            print(f"  Спред: {r['spread_percent']}%")
            print(f"  Чистая: {r['net_profit_percent']}%")
            print(f"  Сигнал: {'✅ ДА' if r['opportunity'] else '❌ НЕТ'} (порог {r['threshold']}%)")
    else:
        print(f"  Нет данных (только spot или только linear)")
    print()