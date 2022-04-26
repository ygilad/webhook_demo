import json
import os

import requests
import hashlib
import hmac
from lambda_function import build_signature_payload, get_secret, get_utc_timestemp_now, TIMESTAMP_DIFF_TOLERANCE_SEC


## Note: Environment varibles to define:
# From Lambda:
#   TIMESTAMP_DIFF_TOLERANCE_SEC
#   MY_SECRET
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://qficjp24rc2dcsupejtzbayc5u0uderj.lambda-url.eu-west-1.on.aws/')


def call_webhook():
    payload = {'somekey': 'somevalue'}

    payload_str = json.dumps(payload)

    timestamp = get_utc_timestemp_now()

    sig_payload = build_signature_payload('POST', WEBHOOK_URL, payload_str, timestamp)
    signature = hmac.new(get_secret(), sig_payload, hashlib.sha256).hexdigest()

    headers = {
        'X-Papaya-Signature': signature,
        'X-Papaya-Request-Timestamp': str(timestamp),
    }
    x = requests.post(WEBHOOK_URL, data=payload_str, headers=headers)
    # x = requests.post(url, data=payload_str, headers={'x-papaya-signature': signature})

    print(x.text)
    print(f"Status Code: {x.status_code}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    call_webhook()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
