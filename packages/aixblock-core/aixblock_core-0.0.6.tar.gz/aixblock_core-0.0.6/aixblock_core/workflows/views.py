import time
import jwt
from core.settings.base import BASE_BACKEND_URL
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from workflows.function import get_external_project_id, get_key, create_key


def workflows_token(request):
    key = get_key()

    if key is None:
        raise Exception("No workflow signing key found")

    current_time = int(time.time())
    token = Token.objects.filter(user=request.user.id).first()

    payload = {
        "version": "v3",
        "externalUserId": request.user.email,
        "externalProjectId": get_external_project_id(request.user),
        "firstName": request.user.first_name,
        "lastName": request.user.last_name,
        "exp": current_time + (30 * 86400),  # Expire in 30 days
        "token": token.key if token else "",
        "url": BASE_BACKEND_URL,
    }

    token = jwt.encode(
        payload,
        key["privateKey"],
        algorithm="RS256",
        headers={"kid": key["id"]},
    )

    return HttpResponse(token)