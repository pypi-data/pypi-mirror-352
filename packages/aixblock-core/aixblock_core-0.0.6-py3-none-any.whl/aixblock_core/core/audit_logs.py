import requests
from django.conf import settings


def send_audit_log(url, data):
    if not url or not settings.AUDIT_TOKEN or not settings.AUDIT_LOGS:
        return

    try:
        r = requests.post(
            url=settings.AUDIT_LOGS + url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AUDIT_TOKEN}"
            },
            json=data,
        )

        if not r.ok:
            print('[AUDIT-LOG] Failed to send')
            print(r.text)
        else:
            print('[AUDIT-LOG] Sent')
    except Exception as e:
        print(e)
