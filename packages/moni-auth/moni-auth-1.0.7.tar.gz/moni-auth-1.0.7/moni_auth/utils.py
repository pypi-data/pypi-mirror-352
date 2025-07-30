from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string

from .permissions import decode_jwt


def generate_random_password() -> str:
    """Generates a random password to be used for a new django admin user

    Returns:
        str: password
    """
    password_length = 12
    allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    password = make_password(get_random_string(password_length, allowed_chars))
    return password


def get_products_keys() -> list:
    """
        Returns a list of the keys of the products defined in settings.MONI_AUTH["PRODUCTS"]
    """
    return [value for key, value in settings.MONI_AUTH["PRODUCTS"].items()]


def get_pages_keys() -> list:
    """
        Returns a list of the keys of the pages defined in settings.MONI_AUTH["PAGES"]
    """
    return [value for key, value in settings.MONI_AUTH["PAGES"].items()]


def get_actions_keys() -> list:
    """
        Returns a list of the keys of the actions defined in settings.MONI_AUTH["ACTIONS"]
    """
    return [value for key, value in settings.MONI_AUTH["ACTIONS"].items()]


def get_email_and_id(request) -> tuple:
    """
        Returns a tuple with the email and id of the logged in user
    """
    if not settings.MONI_AUTH["JWT_DEBUG"]:
        decoded_token = decode_jwt(request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"]))
        return decoded_token["email"], decoded_token["sub"]
    else:
        return 'debug@moni.com.ar', '1'


def get_or_create_user(email, superuser=True, staff=True):
    """ Obtains or creates a user with the given email

    Args:
        email (str): user email

    Returns:
        user: User object
    """
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(email, email, generate_random_password())
        user.is_superuser = superuser
        user.is_staff = staff
        user.save()
    return user


def get_groups_from_jwt(request) -> list:
    """ Obtains the groups from the JWT

    Args:
        request (request): request object

    Returns:
        list: list of groups
    """
    if not settings.MONI_AUTH["JWT_DEBUG"]:
        decoded_token = decode_jwt(request.COOKIES.get(settings.MONI_AUTH["JWT_KEY"]))
        return decoded_token.get("roles", [])
    else:
        return ["superadmin"]
