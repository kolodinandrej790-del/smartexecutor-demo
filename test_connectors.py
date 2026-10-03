# test_connectors.py — проверка всех трёх коннекторов
from submodules.binance_connector import BinanceConnector
from submodules.bybit_connector import BybitConnector
from submodules.okx_connector import OKXConnector

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

print("=== Сравнение цен BTC ===")
print(f"Binance: {binance.get_price('BTCUSDT')}")
print(f"Bybit:   {bybit.get_price('BTCUSDT')}")
print(f"OKX:     {okx.get_price('BTC-USDT')}")

print("\n=== Сравнение цен XAUT ===")
print(f"Binance: {binance.get_price('XAUTUSDT')}")
print(f"Bybit:   {bybit.get_price('XAUTUSDT')}")
print(f"OKX:     {okx.get_price('XAUT-USDT')}")