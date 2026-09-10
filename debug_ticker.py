import sys
sys.path.append('.')

from submodules.okx_connector import OKXConnector

with open('keys.txt') as f:
    lines = f.readlines()

keys = {}
for line in lines:
    line = line.strip()
    if '=' in line:
        k, v = line.split('=', 1)
        keys[k.strip()] = v.strip()

c = OKXConnector(
    api_key=keys.get('OKX_API_KEY',''),
    secret_key=keys.get('OKX_SECRET_KEY',''),
    passphrase=keys.get('OKX_PASSPHRASE','')
)

print("Запрос тикера...")
ticker = c.get_ticker('ETH-USDT')
print(ticker)

print("\nЗапрос свечей...")
klines = c.get_klines('ETH-USDT')
print(klines)