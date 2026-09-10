import requests, json, base64, hmac, hashlib
from datetime import datetime, timezone

with open('keys.txt') as f:
    lines = f.readlines()

keys = {}
for line in lines:
    line = line.strip()
    if '=' in line:
        k, v = line.split('=', 1)
        keys[k.strip()] = v.strip()

api_key = keys['OKX_API_KEY']
secret = keys['OKX_SECRET_KEY']
phrase = keys['OKX_PASSPHRASE']

timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + str(int(datetime.now(timezone.utc).microsecond/1000)).zfill(3) + 'Z'
method = 'POST'
path = '/api/v5/trade/order'
body = json.dumps({
    "instId": "ETH-USDT",
    "tdMode": "cash",
    "side": "sell",
    "ordType": "market",
    "sz": "0.002"
})

def sign(ts, method, path, body):
    msg = ts + method + path + body
    mac = hmac.new(secret.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

signature = sign(timestamp, method, path, body)
headers = {
    'OK-ACCESS-KEY': api_key,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': phrase,
    'Content-Type': 'application/json'
}

resp = requests.post('https://www.okx.com' + path, headers=headers, data=body)
print(json.dumps(resp.json(), indent=2))