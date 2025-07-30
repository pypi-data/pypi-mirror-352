from django.conf import settings

from rest_framework.permissions import BasePermission

from .authenticators import decode_jwt


class BaseJWTPermission(BasePermission):
    product = None
    page = None
    action = None

    def has_permission(self, request, view):
        if settings.MONI_AUTH["JWT_DEBUG"]:
            return True

        permissions = {'products': set(), 'pages': set(), 'actions': set()}

        for jwt_key in settings.MONI_AUTH["JWT_KEYS"]:
            decoded_token = decode_jwt(request.COOKIES.get(jwt_key))
            for perm_key, perm_values in decoded_token.get("permissions", {}).items():
                permissions[perm_key].update(perm_values)

        permissions = {k: list(v) for k, v in permissions.items()}

        self.page = getattr(view, "permission_page", None)
        self.action = getattr(view, "permission_action", None)

        if self.product and self.product not in permissions.get("products", []):
            return False

        if self.page and self.page not in permissions.get("pages", []):
            return False

        if self.action and self.action not in permissions.get("actions", []):
            return False

        return True


class HasBackofficePermission(BaseJWTPermission):
    product = settings.MONI_AUTH["PRODUCTS"]["backoffice"]


class HasDjangoAdminPermission(BaseJWTPermission):
    product = settings.MONI_AUTH["PRODUCTS"]["admin_de_django"]


class HasSharedSecretPermission(BasePermission):
    """
    Custom permission to check for a shared secret token in the request header.
    """

    def has_permission(self, request, view):
        secret_token = request.headers.get('X-Shared-Secret')
        return secret_token == settings.MONI_AUTH["SHARED_SECRET_TOKEN"]
