import random
import string

from core.google_login import GoogleRawLoginFlowService
from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.reward_point_register import reward_point_register

class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginApi(PublicApi):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        """ Handling callback for logging and creating user if first login with google.
        """
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Code and state are required."}, status=status.HTTP_400_BAD_REQUEST)

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()

        user_email = id_token_decoded["email"].lower()
        user = User.objects.filter(email=user_email).last()

        # Create new user
        if user is None:
            user = User.objects.create_user(
                email=user_email,
                password=''.join(random.choice(string.ascii_lowercase) for _ in range(12)),
                is_staff=True,
                is_superuser=False
            )

            reward_point_register(user)
        
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        redirect_url = f"{settings.BASE_BACKEND_URL}"

        return HttpResponseRedirect(redirect_url)
