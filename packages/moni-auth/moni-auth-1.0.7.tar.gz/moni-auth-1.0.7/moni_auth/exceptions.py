from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
        Exception handler that serves two purposes:
        - Returns HTTP 401 Unauthorized when the AuthenticationFailed exception is raised.
        This is commonly raised when the JWT is invalid or expired in the JWTAuthentication class.
        - Modifies the message when a PermissionDenied is raised so it has a key-structure format.
    """
    # Call the default exception handler first
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        # Modify the response status code to 401 Unauthorized
        response.status_code = HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        # Modify the response data to add a key-structure
        response.data = {"detail": PermissionDenied.default_code}

    return response
