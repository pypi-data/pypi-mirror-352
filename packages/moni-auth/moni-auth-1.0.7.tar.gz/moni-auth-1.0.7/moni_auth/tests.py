import jwt

from http.cookies import SimpleCookie

from django.conf import settings


from rest_framework.test import APITestCase
from unittest.mock import patch

from .utils import get_pages_keys, get_products_keys, get_actions_keys


class BackofficeAuthenticatedTestCase(APITestCase):
    def setUp(self):
        self._mock_signals()

        payload = {
            "sub": 1,
            "email": "test@moni.com.ar",
            "permissions": {
                "products": get_products_keys(),
                "pages": get_pages_keys(),
                "actions": get_actions_keys(),
            }
        }
        token = jwt.encode(
            payload, settings.MONI_AUTH["JWT_SECRET_KEY"], algorithm="HS256")

        self.client.cookies = SimpleCookie()
        for key in settings.MONI_AUTH["JWT_KEYS"]:
            self.client.cookies[key] = token

    def _mock_signals(self):
        # Mock the signal handlers to do nothing
        patcher1 = patch(
            'moni_auth.signals.django_admin_user_action', lambda *args, **kwargs: None)
        patcher2 = patch(
            'moni_auth.signals.django_admin_user_login', lambda *args, **kwargs: None)
        patcher3 = patch(
            'moni_auth.signals.django_admin_user_logout', lambda *args, **kwargs: None)
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        patcher1.start()
        patcher2.start()
        patcher3.start()
