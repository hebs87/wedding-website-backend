from django.conf import settings
from django.test import TestCase

from data.seed_tests import seed_invitations
from .models import Invitation
from .forms import InvitationForm, GuestForm
from api.serializers import GuestSerializer


#                                              -- FORM TESTS --
class InvitationFormTest(TestCase):
    """ Test module for InvitationForm """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.invitation = seed_invitations().first()
        cls.data = {
            'invitation_uuid': str(cls.invitation.invitation_uuid),
            'responded': True,
            'additional_info': 'Here is some additional info',
        }

    def test_updates_responded_to_true(self):
        """ Confirm we update the 'responded' field """
        self.assertFalse(self.invitation.responded)
        form = InvitationForm(instance=self.invitation, data=self.data)
        form.save()
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.responded)

    def test_updates_additional_info(self):
        """ Confirm we update the 'additional_info' field """
        self.assertIsNone(self.invitation.additional_info)
        form = InvitationForm(instance=self.invitation, data=self.data)
        form.save()
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.additional_info, self.data.get('additional_info', ''))


class GuestFormTest(TestCase):
    """ Test module for GuestForm """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitation = seed_invitations().first()
        cls.guest = invitation.guests.first()
        cls.data = {
            'guest_uuid': str(cls.guest.guest_uuid),
            'name': 'Darth Vader',
            'wedding': True,
            'party': True,
        }

    def test_updates_name(self):
        """ Confirm we update the 'name' field """
        self.assertNotEqual(self.guest.name, self.data.get('name', ''))
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.name, self.data.get('name', ''))

    def test_updates_wedding(self):
        """ Confirm we update the 'wedding' field """
        self.assertFalse(self.guest.wedding)
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.wedding)

    def test_updates_party(self):
        """ Confirm we update the 'party' field """
        self.assertFalse(self.guest.party)
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.party)


#                                              -- MODEL TESTS --
class InvitationTest(TestCase):
    """ Test module for Invitation model """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.temp_invitation = Invitation()
        cls.invitations = seed_invitations(invitation_count=2)
        cls.invitation_1 = cls.invitations.first()
        cls.invitation_1_guests = cls.invitation_1.guests.all()
        cls.invitation_1_guest = cls.invitation_1_guests.first()
        cls.invitation_2 = cls.invitations.last()
        cls.invitation_2_guest = cls.invitation_2.guests.first()
        cls.data = {
            'invitation': {
                'invitation_uuid': str(cls.invitation_1.invitation_uuid),
                'responded': True,
                'additional_info': 'Here is some additional info',
            },
            'guests': [
                {
                    'guest_uuid': str(cls.invitation_1_guests.first().guest_uuid),
                    'name': 'Darth Vader',
                    'wedding': True,
                    'party': True,
                },
                {
                    'guest_uuid': str(cls.invitation_1_guests.last().guest_uuid),
                    'name': 'Obi-Wan Kenobi',
                    'wedding': True,
                    'party': True,
                },
            ],
        }

    #                                                                                                         save(self)
    def test_save_creates_alphanumeric_code(self):
        """ Test we create an alphanumeric code """
        self.assertTrue(self.invitation_1.code.isalnum())

    #                                                                                               get_invitation(code)
    def test_get_invitation_code_not_found_returns_none(self):
        """ Confirm we return None if an invitation with the specified code doesn't exist """
        invitation = self.invitation_1.get_invitation(code='invalid_code')
        self.assertIsNone(invitation)

    def test_get_invitation_returns_invitation(self):
        """ Confirm we return the matching invitation instance on success """
        invitation = self.invitation_1.get_invitation(code=self.invitation_1.code)
        self.assertEqual(invitation, self.invitation_1)

    #                                                                             get_invitation_guest(self, guest_uuid)
    def test_get_invitation_guest_not_found_returns_none(self):
        """ Confirm we return None if a guest with the specified guest_uuid doesn't exist """
        guest = self.invitation_1.get_invitation_guest(guest_uuid=settings.TEST_UUID)
        self.assertIsNone(guest)

    def test_get_invitation_guest_for_another_invitation_returns_none(self):
        """ Confirm we return None when attempting to get a guest for a different invitation """
        guest = self.invitation_1.get_invitation_guest(guest_uuid=self.invitation_2_guest.guest_uuid)
        self.assertIsNone(guest)

    def test_get_invitation_guest_returns_guest(self):
        """ Confirm we return the matching guest instance on success """
        guest = self.invitation_1.get_invitation_guest(guest_uuid=str(self.invitation_1_guest.guest_uuid))
        self.assertEqual(guest, self.invitation_1_guest)

    #                                                                            process_invitation_response(self, data)
    def test_process_invitation_no_invitation_data_returns_error(self):
        """ Confirm we return False and an error message if no invitation data is provided """
        del self.data['invitation']
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertFalse(success)
        self.assertEqual(error, 'Missing invitation or guests data')

    def test_process_invitation_no_guests_data_returns_error(self):
        """ Confirm we return False and an error message if no guests data is provided """
        del self.data['guests']
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertFalse(success)
        self.assertEqual(error, 'Missing invitation or guests data')

    def test_process_invitation_responded_returns_error(self):
        """ Confirm we return False and an error message if the invitation has already been responded to """
        self.invitation_1.responded = True
        self.invitation_1.save()
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertFalse(success)
        self.assertEqual(error, 'It looks like you\'ve already responded to this invitation')

    def test_process_invitation_invalid_guest_returns_error(self):
        """
        Confirm we return False and an error message if an invalid guest is provided (guest for another invitation)
        """
        invalid_guest = {
            'guest_uuid': str(self.invitation_2_guest.guest_uuid),
            'name': 'Obi-Wan Kenobi',
            'wedding': True,
            'party': True,
        }
        self.data['guests'].append(invalid_guest)
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertFalse(success)
        self.assertEqual(error, 'Sorry, we were unable to update the details for some guests, please try again')

    def test_process_invitation_success_updates_guests(self):
        """ Confirm we update the invitation's guests on success """
        self.invitation_1.process_invitation_response(data=self.data)
        guests_data = self.data.get('guests', [])
        excluded_fields = ['guest_uuid', 'party_only']
        fields = [field for field in GuestSerializer.Meta.fields if field not in excluded_fields]
        for index, guest in enumerate(self.invitation_1.guests.all()):
            guest_data = guests_data[index]
            guest.refresh_from_db()
            for field in fields:
                self.assertEqual(getattr(guest, field), guest_data.get(field, ''))

    def test_process_invitation_success_updates_invitation(self):
        """ Confirm we update the invitation on success """
        self.invitation_1.process_invitation_response(data=self.data)
        invitation_data = self.data.get('invitation', {})
        self.invitation_1.refresh_from_db()
        self.assertTrue(self.invitation_1.responded)
        self.assertEqual(self.invitation_1.additional_info, invitation_data.get('additional_info', ''))

    def test_process_invitation_success_returns_true(self):
        """ Confirm we return True and an empty error message on success """
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertTrue(success)
        self.assertEqual(error, '')


class GuestTest(TestCase):
    """ Test module for Guest model """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations()
        cls.invitation = invitations.first()
        cls.invitation.responded = True
        cls.invitation.save()
        invitation_guests = cls.invitation.guests.all()
        cls.guest_1 = invitation_guests.first()

    #                                                                                                          @property
    #                                                                                             attending_status(self)
    def test_attending_status_pending(self):
        """ Confirm we return 'Pending' if the invitation has not been responded to """
        # Update the invitation's responded status to False
        self.invitation.responded = False
        self.invitation.save()
        self.assertEqual(self.guest_1.attending_status, 'Pending')

    def test_attending_status_wedding_only(self):
        """ Confirm we return 'Wedding only' if wedding=True and party=False """
        # Update the guest's wedding to True
        self.guest_1.wedding = True
        self.guest_1.save()
        self.assertEqual(self.guest_1.attending_status, 'Wedding only')

    def test_attending_status_party_only(self):
        """ Confirm we return 'Party only' if wedding=False and party=True """
        # Update the guest's party to True
        self.guest_1.party = True
        self.guest_1.save()
        self.assertEqual(self.guest_1.attending_status, 'Party only')

    def test_attending_status_both(self):
        """ Confirm we return 'Both' if wedding=True and party=True """
        # Update the guest's wedding and party to True
        self.guest_1.wedding = True
        self.guest_1.party = True
        self.guest_1.save()
        self.assertEqual(self.guest_1.attending_status, 'Both')

    def test_attending_status_no(self):
        """ Confirm we return 'No' if wedding=False and party=False """
        # Update the guest's wedding and party to False
        self.guest_1.wedding = False
        self.guest_1.party = False
        self.guest_1.save()
        self.assertEqual(self.guest_1.attending_status, 'No')
