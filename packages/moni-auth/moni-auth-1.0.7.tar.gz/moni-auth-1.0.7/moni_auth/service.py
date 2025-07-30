import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

import requests
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

__all__ = ['AuthenticationService']


class AuthenticationService:
    URL = settings.MONI_AUTH["AUTHENTICATION_SERVICE_URL"]
    SHARED_SECRET_TOKEN = settings.MONI_AUTH["SHARED_SECRET_TOKEN"]
    TIMEOUT = 20

    def send_log(self, log: dict):
        """
            Sends a new log to the authentication service.
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Shared-Secret': self.SHARED_SECRET_TOKEN,
        }
        url = f'{self.URL}/configurations/log/'
        data = json.dumps({"details": log}, cls=DjangoJSONEncoder)
        response = requests.post(
            url=url, data=data, headers=headers, timeout=self.TIMEOUT)
        return Response(status=response.status_code)


class AuthenticationServiceMock:

    def send_log(self, log: dict):
        return Response(status=HTTP_201_CREATED)


if settings.MONI_AUTH["JWT_DEBUG"]:
    AuthenticationService = AuthenticationServiceMock  # noqa
