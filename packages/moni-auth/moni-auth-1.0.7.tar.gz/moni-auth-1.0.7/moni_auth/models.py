from django.db import models


class UserModel(models.Model):
    """
        BaseModel to store the user_id and user_email of the user that is logged in the service.
        Typically used to replace the Django User model instance.
    """

    user_email = models.EmailField(null=True)
    user_auth_id = models.PositiveIntegerField(null=True)

    class Meta:
        abstract = True
