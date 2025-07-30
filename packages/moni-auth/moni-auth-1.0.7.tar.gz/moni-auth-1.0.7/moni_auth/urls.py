from django.urls import path

from .views import PagesPermissionsView, UserInfoView, DeleteDjangoAdminUser

urlpatterns = [
    path(
        f'user/',
        UserInfoView.as_view(),
        name='user-info'
    ),
    path(
        f'permissions/',
        PagesPermissionsView.as_view(),
        name='pages-permissions'
    ),
    path(
        f'delete-user/',
        DeleteDjangoAdminUser.as_view(),
        name='delete-user'
    ),
]
