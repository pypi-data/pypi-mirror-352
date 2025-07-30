from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .service import AuthenticationService


@receiver(post_save, sender=LogEntry)
def django_admin_user_action(sender, instance, **kwargs):
    if settings.ENVIRONMENT == "test":
        return

    # Check if the change was made in the admin site
    if instance.is_change():
        action = 'UPDATED'
    elif instance.is_addition():
        action = 'CREATED'
    elif instance.is_deletion():
        action = 'DELETED'
    else:
        return

    details = {
        "email": instance.user.email,
        "instance": {
            "id": instance.object_id,
            "name": instance.content_type.model,
            "object_repr": instance.object_repr,
        },
        "type": action,
        "message": f"{instance.user.email} {action} an instance of {instance.content_type.model} with ID {instance.object_id}",  # noqa
        "service": settings.MONI_AUTH["SERVICE_NAME"],
        "action_time": instance.action_time,
    }
    AuthenticationService().send_log(details)


@receiver(user_logged_in)
def django_admin_user_login(sender, request, user, **kwargs):
    if settings.ENVIRONMENT == "test":
        return

    action = "LOGGED IN"
    details = {
        "email": user.email,
        "type": action,
        "message": f"{user.email} has {action} into the {settings.MONI_AUTH['SERVICE_NAME']} service",
        "service": settings.MONI_AUTH["SERVICE_NAME"],
        "action_time": timezone.now()
    }
    AuthenticationService().send_log(details)


@receiver(user_logged_out)
def django_admin_user_logout(sender, request, user, **kwargs):
    if settings.ENVIRONMENT == "test":
        return

    action = "LOGGED OUT"
    details = {
        "email": user.email,
        "type": action,
        "message": f"{user.email} has {action} from the {settings.MONI_AUTH['SERVICE_NAME']} service",
        "service": settings.MONI_AUTH["SERVICE_NAME"],
        "action_time": timezone.now(),
    }
    AuthenticationService().send_log(details)
