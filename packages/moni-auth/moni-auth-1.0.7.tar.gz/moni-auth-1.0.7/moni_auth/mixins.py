from django.conf import settings

from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from .authenticators import JWTAuthentication
from .permissions import HasBackofficePermission


class ConfigurationError(APIException):
    status_code = 500  # Internal Server Error
    default_detail = "Misconfigured view: cannot determine permission action."
    default_code = 'misconfigured_view'


class BasePermissionMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasBackofficePermission]

    permission_page = None
    permission_action_list = None
    permission_action_retrieve = None
    permission_action_create = None
    permission_action_patch = None
    permission_action_put = None
    permission_action_delete = None

    def set_permissions_from_mapping(self, parameter_value, mappings):
        for mapping in mappings:
            if mapping.get('value') == parameter_value:
                for attr, value in mapping.items():
                    if attr != 'value':
                        setattr(self, attr, value)
                break

    def get_permissions(self):
        if settings.MONI_AUTH["JWT_DEBUG"]:
            return super().get_permissions()

        action_permission_mapping = {
            'list': 'permission_action_list',
            'retrieve': 'permission_action_retrieve',
            'create': 'permission_action_create',
            'partial_update': 'permission_action_patch',
            'patch': 'permission_action_patch',
            'put': 'permission_action_patch',
            'update': 'permission_action_put',
            'delete': 'permission_action_delete',
            'get': 'permission_action_list',
            'post': 'permission_action_create',
        }

        # Check if 'action' attribute is available (for ViewSets or ModelViewSets)
        if hasattr(self, 'action'):
            action = self.action

            # Check for custom action permissions
            if action not in action_permission_mapping and hasattr(self, 'custom_action_permissions'):
                custom_permissions = getattr(
                    self, 'custom_action_permissions', {})

                # If a custom action is defined, directly set the permission_action
                if action in custom_permissions:
                    self.permission_action = custom_permissions[action]
                    return super().get_permissions()

        # Check if the view is an instance of APIView or ListAPIView
        elif isinstance(self, (APIView, ListAPIView)):
            action = self.request.method.lower()
        else:
            raise ConfigurationError(
                "Unable to determine action for permission check")

        permission_attribute = action_permission_mapping.get(action)
        if permission_attribute is not None and getattr(self, permission_attribute, None) is not None:
            self.permission_action = getattr(self, permission_attribute)
        else:
            raise ConfigurationError(
                f"No permission attribute mapping found for action: {action}")

        return super().get_permissions()


class ParameterBasedPermissionMixin(BasePermissionMixin):
    """
    Mixin to handle permission logic based on a parameter value.
    """
    parameter_name = None
    parameter_permissions_map = []

    def get_permissions(self):
        parameter_value = self.kwargs.get(self.parameter_name)
        self.set_permissions_from_mapping(
            parameter_value, self.parameter_permissions_map)
        return super().get_permissions()


class DataParameterBasedPermissionMixin(BasePermissionMixin):
    """
    Mixin to handle permission logic based on a parameter value in request data.
    """
    data_parameter_name = None
    data_parameter_permissions_map = []

    def get_permissions(self):
        parameter_value = self.request.data.get(self.data_parameter_name)
        self.set_permissions_from_mapping(
            parameter_value, self.data_parameter_permissions_map)
        return super().get_permissions()
