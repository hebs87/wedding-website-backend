import uuid

from model_utils.models import TimeStampedModel

from django.db import models


# Create your models here.
class Invitation(TimeStampedModel):
    """
    Invitation model to allow creating an invitation for a party
    """
    invitation_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    responded = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

    def __str__(self):
        return f'{self.name} - {self.responded}'


class Guest(TimeStampedModel):
    """
    Guest model to allow creating a guest for an invitation
    """
    guest_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invitation = models.ForeignKey(Invitation, related_name='guests', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    attending = models.BooleanField(default=False)
    song = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return f'{self.name} - {self.attending}'
