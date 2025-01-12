import uuid
import random
import string

from model_utils.models import TimeStampedModel

from django.db import models

from data.constants import RANDOM_STRING_LENGTH


# Create your models here.
class Invitation(TimeStampedModel):
    """
    Invitation model to allow creating an invitation for a party
    """
    invitation_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    responded = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

    def __str__(self):
        return f'{self.name} - {self.responded}'

    def save(self, *args, **kwargs):
        """ Override save() to generate a unique code when creating a new Invitation """
        code = self.generate_random_string()
        while Invitation.objects.filter(code=code).exists():
            code = self.generate_random_string()

        self.code = code

        super(Invitation, self).save(*args, **kwargs)

    @staticmethod
    def generate_random_string(length=RANDOM_STRING_LENGTH):
        """ Generate a random alphanumeric string of a specified length """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()

    @staticmethod
    def get_invitation(code):
        """ Get an invitation by code """
        try:
            invitation = Invitation.objects.get(code=code)
        except Invitation.DoesNotExist:
            invitation = None

        return invitation


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
