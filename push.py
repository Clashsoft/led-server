import json
from pywebpush import webpush, WebPushException

with open('private_key.txt') as private_key:
    VAPID_PRIVATE_KEY = private_key.readline().strip()
with open('public_key.txt') as public_key:
    VAPID_PUBLIC_KEY = public_key.readline().strip()

VAPID_CLAIMS = {'sub': 'mailto:clashsoft@hotmail.com'}


def send_web_push(subscription_info, message_body):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(message_body),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
    except WebPushException as ex:
        print(ex)
