from django.forms import ModelForm

from .models import Invitation, Guest


class InvitationForm(ModelForm):
    """ A custom form for updating an Invitation instance """

    class Meta:
        model = Invitation
        fields = ('responded', 'additional_info')


class GuestForm(ModelForm):
    """ A custom form for updating a Guest instance """

    class Meta:
        model = Guest
        fields = ('name', 'wedding', 'party')
