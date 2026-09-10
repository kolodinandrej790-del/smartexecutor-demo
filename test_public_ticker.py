import requests, json

# Публичный запрос без подписи
resp = requests.get('https://www.okx.com/api/v5/market/ticker', params={'instId': 'ETH-USDT'})
print(json.dumps(resp.json(), indent=2))