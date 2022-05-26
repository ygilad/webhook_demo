import datetime
import json
import base64
import hashlib
import hmac
import os

## Note: Environment varibles to define:
TIMESTAMP_DIFF_TOLERANCE_SEC = os.environ.get('TIMESTAMP_DIFF_TOLERANCE_SEC', 5 * 60)
MY_SECRET = os.environ.get('MY_SECRET', '2good2b4go10')  # TODO: replace with proper secret read.

def get_secret():
    return bytify(MY_SECRET)


def build_response(event, error=False):
    resp = dict(event=event)
    if error:
        resp['error'] = error
    resp_body = json.dumps(resp, indent=4, sort_keys=True)
    print(resp_body)

    # Handle lambda edge endpoint
    return {
        'statusCode': 401 if error else 200,
        'body': resp_body,
        'isBase64Encoded': False
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
    protocol = event['headers'].get('x-forwarded-proto', 'https')
    domainName = event['requestContext']['domainName']

    http_metadata = event['requestContext'].get("http", None)
    if http_metadata:
        # Handle lambda edge endpoint
        method = http_metadata['method']
        path = http_metadata['path']
    else:
        # Handle api gateway custom mapping
        method = event['requestContext']['httpMethod']
        path = event['requestContext']['path']

    url = f'{protocol}://{domainName}{path}'
    return build_signature_payload(method, url, body, timestamp)


def bytify(item):
    if type(item) == str:
        return bytes(item, 'utf-8')
    return item


def event_header_get(event_header, header_key, default=None):
    return event_header.get(header_key, event_header.get(header_key.lower(), default))


def lambda_handler(event, context):
    print(event)

    request_signature = event_header_get(event['headers'], 'X-Papaya-Signature')
    if not request_signature:
        return build_response(event, error="No signature header")

    request_timestamp = event_header_get(event['headers'], 'X-Papaya-Request-Timestamp')
    if not request_timestamp:
        return build_response(event, error="No request timestamp header")
    if abs(int(request_timestamp) - get_utc_timestemp_now()) > TIMESTAMP_DIFF_TOLERANCE_SEC:
        return build_response(event, error="Difference too big in timestemp")

    body = event.get('body', b"")
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body)
    if type(body) is dict:
        body = bytify(json.dumps(body))

    sig_payload = build_signature_payload_from_event(event, body, request_timestamp)
    try:
        signature = hmac.new(get_secret(), sig_payload, hashlib.sha256).hexdigest()

        if signature != request_signature:
            return build_response(event, error="Bad signature")
    except Exception as e:
        return build_response(event, error="Exception: " + str(e))

    return build_response(event)
