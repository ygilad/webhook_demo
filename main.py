import json
import os

import requests
import hashlib
import hmac
from lambda_function import build_signature_payload, get_secret, get_utc_timestemp_now


## Note: Environment varibles to define:
# From Lambda:
#   TIMESTAMP_DIFF_TOLERANCE_SEC
#   MY_SECRET
WEBHOOK_BASE_URL = os.environ.get('WEBHOOK_BASE_URL', 'https://qficjp24rc2dcsupejtzbayc5u0uderj.lambda-url.eu-west-1.on.aws/webhooks')
WEBHOOK_BASE_URL = os.environ.get('WEBHOOK_BASE_URL', 'https://ewvzojil9e.execute-api.eu-west-1.amazonaws.com/DemoStage/webhooks')

def call_webhook(event_path, payload):
    webhook_url = WEBHOOK_BASE_URL + event_path

    payload_str = json.dumps(payload)

    timestamp = get_utc_timestemp_now()

    sig_payload = build_signature_payload('POST', webhook_url, payload_str, timestamp)
    signature = hmac.new(get_secret(), sig_payload, hashlib.sha256).hexdigest()

    headers = {
        'X-Papaya-Signature': signature,
        'X-Papaya-Request-Timestamp': str(timestamp),
    }
    x = requests.post(webhook_url, data=payload_str, headers=headers)

    print(x.text)
    print(f"Status Code: {x.status_code}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # call first webhook
    call_webhook(
        "/eor/signed_contract_uploaded",
        {
            "metadata": {  # metadata object is optional
                "event_name": "eor_signed_contract_uploaded",  # fixed input (hardcoded) no need to read from system
                "sf_env": "papaya_partial",
            },
            "sf_eor_id": "r84h8",
            "request_id": "d8gr4g4g8",
            "upload_timestamp": "2022-05-18T14:24:00.000+03:00",
            "upload_status": "completed",
        }
    )

    # call second webhook
    call_webhook(
        "/eor/request_approved",
        {
            "metadata": {  # metadata object is optional
                "event_name": "eor_request_approved",  # fixed input (hardcoded) no need to read from system
                "sf_env": "papaya_partial",
            },
            "sf_eor_id": "r84h8",
            "request_id": "d8gr4g4g8",
            "eor_request_status": "completed",
            "issue_deposit": False,
            "timestamp": "2022-05-18T14:24:00.000+03:00",
        }
    )

