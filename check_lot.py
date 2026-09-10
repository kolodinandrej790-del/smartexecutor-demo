import requests, json

resp = requests.get(
    'https://www.okx.com/api/v5/public/instruments',
    params={'instType': 'SPOT', 'instId': 'ETH-USDT'}
)
data = resp.json()

if data.get('code') == '0' and data.get('data'):
    inst = data['data'][0]
    print('Инструмент:', inst['instId'])
    print('Минимальный размер сделки (minSz):', inst.get('minSz'))
    print('Шаг размера (lotSz):', inst.get('lotSz'))
    print('Минимальная сумма (minNotional):', inst.get('minNotional'))
else:
    print('Ошибка:', json.dumps(data, indent=2))