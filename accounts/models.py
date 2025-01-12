import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from model_utils.models import TimeStampedModel


class ActiveManager(models.Manager):
    """
    Enable retrieving queryset of active users
    """

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


USER_ROLES = (
    ('admin', 'Admin'),
    ('user', 'User'),
)


class WeddingWebsiteBaseUser(AbstractUser):
    """
    WeddingWebsiteBaseUser model to allow creating a base user
    """
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = models.CharField(choices=USER_ROLES, max_length=30, blank=False, default='admin')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)

        # save original values, when model is loaded from database,
        # in a separate attribute on the model
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        """ Override save() to set superuser and staff status for ballerz_admin to allow access to admin panel """
        if self.role == 'admin':
            self.is_superuser = True
            self.is_staff = True
        super(WeddingWebsiteBaseUser, self).save(*args, **kwargs)
