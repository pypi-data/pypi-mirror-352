from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .authenticators import JWTAuthentication, decode_jwt
from .permissions import (
    HasBackofficePermission,
    HasDjangoAdminPermission,
    HasSharedSecretPermission,
)
from .utils import get_or_create_user, get_pages_keys, get_actions_keys


class CustomAdminLoginView(LoginView):
    """Custom Django Admin Login. It will validate through the JWT that receives in the cookie if the user
    has permission to enter the Admin. There's three possible outputs:
    - The user doesn't have permissions: it won't allow the user to enter and it will show a error message
    - The user has an invalid token: it will be redirected to the authentication backoffice
    - The user has permissions and a valid token: it will be automatically logged in. If the user doesn't exist
    it will be created.
    """

    def dispatch(self, request, *args, **kwargs):
        jwt_authenticator = JWTAuthentication()
        jwt_permission = HasDjangoAdminPermission()
        try:
            jwt_authenticator.authenticate(request)
            if not jwt_permission.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to access the admin panel.")
        except AuthenticationFailed:
            redirect_url = f"{settings.MONI_AUTH['BO_AUTH_LOGIN_URL']}?next={request.build_absolute_uri(reverse('admin:index'))}"  # noqa
            return redirect(redirect_url)

        decoded_token = decode_jwt(
            request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"]))

        if settings.MONI_AUTH["JWT_DEBUG"]:
            email = "debug@moni.com.ar"
        else:
            email = decoded_token['email']

        user = get_or_create_user(email)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        # Redirect to admin dashboard
        return HttpResponseRedirect(reverse('admin:index'))


class DeleteDjangoAdminUser(APIView):
    """
       Deletes a Django Admin user. This is used by the authentication service after a user is deleted.
    """

    permission_classes = [HasSharedSecretPermission]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Missing username'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            user.delete()
            return Response({'message': f'User {username} deleted successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasBackofficePermission]

    def get(self, request):
        """Returns the user information that is stored in the JWT.
        If JWT_DEBUG is True then it will return a fake user.
        """
        if settings.MONI_AUTH["JWT_DEBUG"]:
            user = {
                "email": "debug@moni.com.ar",
                "id": "1",
            }
        else:
            try:
                decoded_token = decode_jwt(
                    request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"]))
                user = {
                    "email": decoded_token.get("email", ""),
                    "id": decoded_token.get("sub", ""),
                }
            except AttributeError:
                raise AuthenticationFailed("invalid_user_info")

        return Response(status=status.HTTP_200_OK, data=user)


class PagesPermissionsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasBackofficePermission]

    def get(self, request):
        """Returns all the pages that the user has access to. According to this the backoffice
        will show or not the links on the drawer.
        If JWT_DEBUG is True then it will return all the pages and it won't check for any JWT.
        """

        actions_param = request.query_params.get('actions', False)

        if settings.MONI_AUTH.get("JWT_DEBUG", False):
            # Return pages or actions based on the 'actions' query parameter
            permissions = self._get_debug_permissions(actions_param)
        else:
            try:
                jwt_token = request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"])
                decoded_token = decode_jwt(jwt_token)
                permissions = self._get_permissions(decoded_token, actions_param)
            except (AttributeError, KeyError):
                permissions = []
        return Response(status=status.HTTP_200_OK, data=permissions)

    def _get_debug_permissions(self, actions_param: bool) -> list:
        """Returns permissions based on the debug mode and query parameters."""
        if actions_param:
            return get_actions_keys()
        return get_pages_keys()

    def _get_permissions(self, decoded_token, actions_param):
        """Helper method to extract permissions based on actions or pages."""
        if actions_param:
            actions = decoded_token.get('permissions', {}).get('actions', [])
            return [action for action in actions if action in settings.MONI_AUTH['ACTIONS'].values()]
        pages = decoded_token.get('permissions', {}).get('pages', [])
        return [page for page in pages if page.startswith(settings.MONI_AUTH["PRODUCTS"]["backoffice"])]
