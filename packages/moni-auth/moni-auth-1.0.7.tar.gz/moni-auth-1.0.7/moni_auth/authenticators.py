from django.conf import settings

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if settings.MONI_AUTH["JWT_DEBUG"]:
            return

        try:
            decoded_token = decode_jwt(
                request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"]))
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("expired_token")
        except jwt.DecodeError:
            raise AuthenticationFailed("invalid_token")

        return decoded_token["sub"], decoded_token


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.MONI_AUTH["JWT_SECRET_KEY"], algorithms=["HS256"])
