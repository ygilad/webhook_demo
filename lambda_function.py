import datetime
import json
import base64
import hashlib
import hmac
import os

## Note: Environment varibles to define:
TIMESTAMP_DIFF_TOLERANCE_SEC = os.environ.get('TIMESTAMP_DIFF_TOLERANCE_SEC', 5 * 60)
MY_SECRET = os.environ.get('MY_SECRET', '2good2b4go10')


def get_secret():
    return bytify(MY_SECRET)


def build_response(event, error=False):
    resp = dict(event=event)
    if error:
        resp['error'] = error

    resp_body = json.dumps(resp, indent=4, sort_keys=True)
    print(resp_body)
    return {
        'statusCode': 401 if error else 200,
        'body': resp_body,
    }


def build_signature_payload(method, url, body, timestamp):
    payload = bytify(f'{method}{url}')
    payload += bytify(body)
    payload += bytify(str(timestamp))
    return payload


def get_utc_timestemp_now():
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_timestamp = dt.timestamp()
    return int(utc_timestamp)


def build_signature_payload_from_event(event, body, timestamp):
    method = event['requestContext']['http']['method']
    protocol = event['headers'].get('x-forwarded-proto', 'https')
    domainName = event['requestContext']['domainName']
    path = event['requestContext']['http']['path']

    url = f'{protocol}://{domainName}{path}'
    return build_signature_payload(method, url, body, timestamp)


def bytify(item):
    if type(item) == str:
        return bytes(item, 'utf-8')
    return item


def lambda_handler(event, context):
    request_signature = event['headers'].get('X-Papaya-Signature'.lower(), None)
    if not request_signature:
        return build_response(event, error="No signature header")

    request_timestamp = event['headers'].get('X-Papaya-Request-Timestamp'.lower(), None)
    if not request_timestamp:
        return build_response(event, error="No request timestamp header")
    if abs(int(request_timestamp) - get_utc_timestemp_now()) > TIMESTAMP_DIFF_TOLERANCE_SEC:
        return build_response(event, error="Difference too big in timestemp")


    body = event.get('body', b"")
    if event['isBase64Encoded']:
        body = base64.b64decode(body)

    sig_payload = build_signature_payload_from_event(event, body, request_timestamp)
    try:
        signature = hmac.new(get_secret(), sig_payload, hashlib.sha256).hexdigest()

        if signature != request_signature:
            return build_response(event, error="Bad signature")
    except Exception as e:
        return build_response(event, error="Exception: " + str(e))

    return build_response(event)
