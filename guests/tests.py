from django.conf import settings
from django.test import TestCase

from data.seed_tests import seed_invitations
from data.constants import RANDOM_STRING_LENGTH
from .models import Invitation, Guest
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
            'attending': True,
            'song': 'The Imperial March',
        }

    def test_updates_name(self):
        """ Confirm we update the 'name' field """
        self.assertNotEqual(self.guest.name, self.data.get('name', ''))
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.name, self.data.get('name', ''))

    def test_updates_attending(self):
        """ Confirm we update the 'attending' field """
        self.assertFalse(self.guest.attending)
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertTrue(self.guest.attending)

    def test_updates_song(self):
        """ Confirm we update the 'song' field """
        self.assertNotEqual(self.guest.song, self.data.get('song', ''))
        form = GuestForm(instance=self.guest, data=self.data)
        form.save()
        self.guest.refresh_from_db()
        self.assertEqual(self.guest.song, self.data.get('song', ''))


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
                    'attending': True,
                    'song': 'The Imperial March',
                },
                {
                    'guest_uuid': str(cls.invitation_1_guests.last().guest_uuid),
                    'name': 'Obi-Wan Kenobi',
                    'attending': True,
                    'song': 'Star Wars (Main Theme)',
                },
            ],
        }

    #                                                                                                         save(self)
    def test_save_creates_alphanumeric_code(self):
        """ Test we create an alphanumeric code """
        self.assertTrue(self.invitation_1.code.isalnum())

    #                                                                                  generate_random_string(length=10)
    def test_generate_random_string_default(self):
        """ Confirm we return an alphanumeric string, same length as RANDOM_STRING_LENGTH, by default """
        random_string = self.invitation_1.generate_random_string()
        self.assertEqual(len(random_string), RANDOM_STRING_LENGTH)
        self.assertTrue(random_string.isalnum())

    def test_generate_random_string_custom_length(self):
        """ Confirm we return an alphanumeric string by of custom length when we specify length arg """
        custom_length = 5
        random_string = self.invitation_1.generate_random_string(length=custom_length)
        self.assertEqual(len(random_string), custom_length)
        self.assertTrue(random_string.isalnum())

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
            'attending': 'Star Wars (Main Theme)',
        }
        self.data['guests'].append(invalid_guest)
        success, error = self.invitation_1.process_invitation_response(data=self.data)
        self.assertFalse(success)
        self.assertEqual(error, 'Sorry, we were unable to update the details for some guests, please try again')

    def test_process_invitation_success_updates_guests(self):
        """ Confirm we update the invitation's guests on success """
        self.invitation_1.process_invitation_response(data=self.data)
        guests_data = self.data.get('guests', [])
        excluded_fields = ['guest_uuid', 'meal']
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

    #                                                                            responded_invitations(responded_status)
    def test_responded_invitations_responded_status_true_no_results_returns_empty_queryset(self):
        """ Confirm we return an empty queryset if no responded invitations are found, if responded_status=True """
        invitations = self.temp_invitation.responded_invitations(responded_status=True)
        self.assertFalse(invitations.count())

    def test_responded_invitations_responded_status_true_returns_responded_invitations(self):
        """ Confirm we only return responded invitations, if responded_status=True """
        # Update invitation_1 to responded=True
        self.invitation_1.responded = True
        self.invitation_1.save()
        invitations = self.temp_invitation.responded_invitations(responded_status=True)
        # invitation_1 should be the only responded invitation
        self.assertEqual(invitations.count(), 1)
        self.assertEqual(invitations.first(), self.invitation_1)

    def test_responded_invitations_responded_status_false_no_results_returns_empty_queryset(self):
        """
        Confirm we return an empty queryset if no invitations pending response are found, if responded_status=False
        """
        # Update all invitations to responded=True
        self.invitations.update(responded=True)
        invitations = self.temp_invitation.responded_invitations(responded_status=False)
        self.assertFalse(invitations.count())

    def test_responded_invitations_responded_status_false_returns_pending_response_invitations(self):
        """ Confirm we only return invitations pending response, if responded_status=False """
        # Update invitation_1 to responded=True
        self.invitation_1.responded = True
        self.invitation_1.save()
        invitations = self.temp_invitation.responded_invitations(responded_status=False)
        # invitation_2 should be the only invitation pending response
        self.assertEqual(invitations.count(), 1)
        self.assertEqual(invitations.first(), self.invitation_2)


class GuestTest(TestCase):
    """ Test module for Guest model """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.temp_guest = Guest()
        invitations = seed_invitations()
        cls.invitation = invitations.first()
        cls.invitation.responded = True
        cls.invitation.save()
        cls.invitation_guests = cls.invitation.guests.all()
        cls.guest_1 = cls.invitation_guests.first()
        cls.guest_2 = cls.invitation_guests.last()

    #                                                                                 attending_guests(attending_status)
    def test_attending_guests_attending_status_true_invitation_responded_false_returns_empty_queryset(self):
        """ Confirm we return an empty queryset if invitation hasn't been responded to, if attending_status=True """
        # Update all guests to attending=True but invitation to responded=False
        self.invitation.responded = False
        self.invitation.save()
        self.invitation_guests.update(attending=True)
        guests = self.temp_guest.attending_guests(attending_status=True)
        self.assertFalse(guests.count())

    def test_attending_guests_attending_status_true_no_results_returns_empty_queryset(self):
        """ Confirm we return an empty queryset if no attending guests are found, if attending_status=True """
        # All test guests have attending=False by default
        guests = self.temp_guest.attending_guests(attending_status=True)
        self.assertFalse(guests.count())

    def test_attending_guests_attending_status_true_returns_attending_guests(self):
        """ Confirm we only return attending guests, if attending_status=True """
        # Update guest_2 to attending=True
        self.guest_2.attending = True
        self.guest_2.save()
        guests = self.temp_guest.attending_guests(attending_status=True)
        self.assertEqual(guests.count(), 1)
        self.assertEqual(guests.first(), self.guest_2)

    def test_attending_guests_attending_status_false_invitation_responded_false_returns_empty_queryset(self):
        """ Confirm we return an empty queryset if invitation hasn't been responded to, if attending_status=False """
        # Update invitation to responded=False, all guests already have attending=False
        self.invitation.responded = False
        self.invitation.save()
        guests = self.temp_guest.attending_guests(attending_status=False)
        self.assertFalse(guests.count())

    def test_attending_guests_attending_status_false_no_results_returns_empty_queryset(self):
        """ Confirm we return an empty queryset if no attending guests are found, if attending_status=False """
        # Updating all guests to attending=True
        self.invitation_guests.update(attending=True)
        guests = self.temp_guest.attending_guests(attending_status=False)
        self.assertFalse(guests.count())

    def test_attending_guests_attending_status_false_returns_not_attending_guests(self):
        """ Confirm we only return guests who are not attending, if attending_status=False """
        # Update guest_2 to attending=True
        self.guest_2.attending = True
        self.guest_2.save()
        guests = self.temp_guest.attending_guests(attending_status=False)
        self.assertEqual(guests.count(), 1)
        self.assertEqual(guests.first(), self.guest_1)
