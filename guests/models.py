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

    def get_invitation_guest(self, guest_uuid):
        """ Get a guest for an invitation by guest_uuid """
        try:
            guest = self.guests.get(guest_uuid=guest_uuid)
        except:
            guest = None

        return guest

    def process_invitation_response(self, data):
        """ Process the response to an invitation and update the details for each associated guest """
        # Import here to prevent circular import error
        from .forms import InvitationForm, GuestForm

        # Return error if there is no invitation or guests data
        invitation_data = data.get('invitation', {})
        guests_data = data.get('guests', [])
        if not invitation_data or not guests_data:
            return False, 'Missing invitation or guests data'

        # Return error if invitation has already been responded to
        if self.responded:
            return False, 'It looks like you\'ve already responded to this invitation'

        # Update details for each associated guest
        for guest_data in guests_data:
            guest_uuid = guest_data.get('guest_uuid', '')
            try:
                guest = self.get_invitation_guest(guest_uuid=guest_uuid)
                guest_form = GuestForm(instance=guest, data=guest_data)
                guest_form.save()
            except:
                return False, 'Sorry, we were unable to update the details for some guests, please try again'

        try:
            invitation_form = InvitationForm(instance=self, data=invitation_data)
            invitation_form.save()
        except:
            return False, 'Sorry, we were unable to update the details for this invitation, please try again'

        return True, ''

    @staticmethod
    def responded_invitations(responded_status):
        """ Get list of invitations matching the responded status """
        return Invitation.objects.filter(responded=responded_status)


class Guest(TimeStampedModel):
    """
    Guest model to allow creating a guest for an invitation
    """
    guest_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invitation = models.ForeignKey(Invitation, related_name='guests', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    attending = models.BooleanField(default=False)
    song = models.CharField(max_length=255, blank=True, null=True)
    meal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'

    def __str__(self):
        return f'{self.name} - {self.attending}'

    @staticmethod
    def attending_guests(attending_status):
        """ Get list of guests matching the attending status, for responded invitations """
        return Guest.objects.filter(attending=attending_status, invitation__responded=True)
