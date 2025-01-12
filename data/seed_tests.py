from guests.models import Invitation, Guest


def seed_guests(invitation, guests_count=1):
    """ Create guests """
    for i in range(guests_count):
        Guest.objects.create(
            invitation=invitation,
            name=f'Guest {i + 1}',
            song=f'Song {i + 1}'
        )


def seed_invitations(invitation_count=1):
    """ Create invitations and 2 guests per invitation """
    for i in range(invitation_count):
        invitation = Invitation.objects.create(
            name=f'Invitation {i + 1}'
        )
        seed_guests(invitation=invitation, guests_count=2)

    return Invitation.objects.all()
