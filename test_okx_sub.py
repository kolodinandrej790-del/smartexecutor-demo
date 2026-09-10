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
method = 'GET'
path = '/api/v5/account/balance'

def sign(ts, method, path):
    msg = ts + method + path
    mac = hmac.new(secret.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

signature = sign(timestamp, method, path)
headers = {
    'OK-ACCESS-KEY': api_key,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': phrase,
    'OK-ACCESS-SUBACCOUNT': 'SmartExecutor',
    'Content-Type': 'application/json'
}

resp = requests.get('https://www.okx.com' + path, headers=headers)
print(json.dumps(resp.json(), indent=2))