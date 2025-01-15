from django.test import TestCase, Client
from django.urls import reverse

from guests.models import Guest
from api.serializers import GuestSerializer, InvitationSerializer
from data.seed_tests import seed_invitations


client = Client()


#                                              -- SERIALIZER TESTS --
class GuestSerializerTest(TestCase):
    """ Test suite for GuestSerializer """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations()
        cls.invitation = invitations.first()
        cls.guest = cls.invitation.guests.first()

    def test_guest_uuid(self):
        """ Confirm we return the 'guest_uuid' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('guest_uuid', ''), str(self.guest.guest_uuid))

    def test_name(self):
        """ Confirm we return the 'name' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('name', ''), self.guest.name)

    def test_attending(self):
        """ Confirm we return the 'attending' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('attending', ''), self.guest.attending)

    def test_song(self):
        """ Confirm we return the 'song' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('song', ''), self.guest.song)

    def test_meal(self):
        """ Confirm we return the 'meal' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('meal', ''), self.guest.meal)


class InvitationSerializerTest(TestCase):
    """ Test suite for InvitationSerializer """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations()
        cls.invitation = invitations.first()
        cls.guests = cls.invitation.guests.all()

    def test_invitation_uuid(self):
        """ Confirm we return the 'invitation_uuid' field """
        serializer = InvitationSerializer(self.invitation).data
        self.assertEqual(serializer.get('invitation_uuid', ''), str(self.invitation.invitation_uuid))

    def test_name(self):
        """ Confirm we return the 'name' field """
        serializer = InvitationSerializer(self.invitation).data
        self.assertEqual(serializer.get('name', ''), self.invitation.name)

    def test_responded(self):
        """ Confirm we return the 'responded' field """
        serializer = InvitationSerializer(self.invitation).data
        self.assertEqual(serializer.get('responded', ''), self.invitation.responded)

    def test_additional_info(self):
        """ Confirm we return the 'code' field """
        serializer = InvitationSerializer(self.invitation).data
        self.assertEqual(serializer.get('additional_info', ''), self.invitation.additional_info)

    def test_guests(self):
        """ Confirm we return the 'guests' field """
        serializer = InvitationSerializer(self.invitation).data
        guests = serializer.get('guests', [])
        self.assertTrue(len(guests))
        fields = GuestSerializer.Meta.fields
        for index, guest in enumerate(guests):
            for field in fields:
                if field == 'guest_uuid':
                    self.assertEqual(guest.get(field, ''), str(getattr(self.guests[index], field)))
                else:
                    self.assertEqual(guest.get(field, ''), getattr(self.guests[index], field))


#                                              -- VIEW TESTS --
class InvitationTest(TestCase):
    """ Test suite for invitation view """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations(invitation_count=2)
        cls.invitation_1 = invitations.first()
        cls.invitation_1_guests = cls.invitation_1.guests.all()
        cls.invitation_1_guest = cls.invitation_1_guests.first()
        invitation_2 = invitations.last()
        cls.invitation_2_guest = invitation_2.guests.first()
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
        cls.failure_kwargs = {'code': 'invalid_code'}
        cls.success_kwargs = {'code': cls.invitation_1.code}

    #                                                                                                      Generic tests
    def test_success(self):
        """ Confirm we return a 200 status code on success """
        response = client.get(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_invitation_not_found_returns_error(self):
        """ Confirm we return an error if an invitation with the specified code doesn't exist """
        response = client.get(
            reverse('api:invitation', kwargs=self.failure_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        self.assertEqual('', response_json.get('Sorry, we can\'t find an invitation with that code', ''))

    #                                                                                                     Get invitation
    def test_get_invitation_success_returns_invitation_data(self):
        """ Confirm we return the invitation data, including guests, on success """
        response = client.get(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        invitation = response_json.get('invitation', {})
        guests = invitation.get('guests', [])
        # Check main invitation data
        invitation_fields = InvitationSerializer.Meta.fields
        self.assertTrue(len(guests))
        for field in invitation_fields:
            if field == 'guests':
                continue
            if field == 'invitation_uuid':
                self.assertEqual(invitation.get(field, ''), str(getattr(self.invitation_1, field)))
            else:
                self.assertEqual(invitation.get(field, ''), getattr(self.invitation_1, field))
        # Check guest data
        guest_fields = GuestSerializer.Meta.fields
        for index, guest in enumerate(guests):
            for field in guest_fields:
                if field == 'guest_uuid':
                    self.assertEqual(guest.get(field, ''), str(getattr(self.invitation_1_guests[index], field)))
                else:
                    self.assertEqual(guest.get(field, ''), getattr(self.invitation_1_guests[index], field))

    #                                                                                              Respond to invitation
    def test_respond_to_invitation_no_invitation_data_returns_error(self):
        """ Confirm we return an error message if no invitation data is provided """
        del self.data['invitation']
        response = client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        self.assertEqual('', response_json.get('Missing invitation or guests data', ''))

    def test_respond_to_invitation_no_guests_data_returns_error(self):
        """ Confirm we return an error message if no guests data is provided """
        del self.data['guests']
        response = client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        self.assertEqual('', response_json.get('Missing invitation or guests data', ''))

    def test_respond_to_invitation_responded_returns_error(self):
        """ Confirm we return an error message if the invitation has already been responded to """
        self.invitation_1.responded = True
        response = client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        self.assertEqual('', response_json.get('It looks like you\'ve already responded to this invitation', ''))

    def test_respond_to_invitation_invalid_guest_returns_error(self):
        """ Confirm we return an error message if an invalid guest is provided (guest for another invitation) """
        invalid_guest = {
            'guest_uuid': str(self.invitation_2_guest.guest_uuid),
            'name': 'Obi-Wan Kenobi',
            'attending': 'Star Wars (Main Theme)',
        }
        self.data['guests'].append(invalid_guest)
        response = client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        self.assertEqual(
            '',
            response_json.get('Sorry, we were unable to update the details for some guests, please try again', '')
        )

    def test_respond_to_invitation_success_updates_guests(self):
        """ Confirm we update the invitation's guests on success """
        client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        guests_data = self.data.get('guests', [])
        for index, guest in enumerate(self.invitation_1.guests.all()):
            guest_data = guests_data[index]
            guest.refresh_from_db()
            self.assertEqual(guest.name, guest_data.get('name', ''))
            self.assertTrue(guest.attending)
            self.assertEqual(guest.song, guest_data.get('song', ''))

    def test_respond_to_invitation_success_updates_invitation(self):
        """ Confirm we update the invitation on success """
        client.post(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
            data=self.data,
        )
        invitation_data = self.data.get('invitation', {})
        self.invitation_1.refresh_from_db()
        self.assertTrue(self.invitation_1.responded)
        self.assertEqual(self.invitation_1.additional_info, invitation_data.get('additional_info', ''))


class AttendingGuestsTest(TestCase):
    """ Test suite for attending_guests view """

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

    #                                                                                                      Generic tests
    def test_success(self):
        """ Confirm we return a 200 status code on success """
        response = client.get(
            reverse('api:attending_guests'),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_success_returns_correct_guests_data(self):
        """ Confirm we return the correct guests serialized data in the response """
        response = client.get(
            reverse('api:attending_guests'),
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        fields = GuestSerializer.Meta.fields
        for guest in guests:
            for field in fields:
                self.assertIn(field, guest)

    #                                                                                                          Attending
    def test_attending_status_true_invitation_responded_false_returns_empty_guests_list(self):
        """ Confirm we return an empty guests list if invitation hasn't been responded to, if ?attending_status=True """
        # Update all guests to attending=True but invitation to responded=False
        self.invitation.responded = False
        self.invitation.save()
        self.invitation_guests.update(attending=True)
        response = client.get(
            f'{reverse("api:attending_guests")}?attending_status=True',
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(guests, [])

    def test_attending_status_true_no_results_returns_empty_guests_list(self):
        """ Confirm we return an empty guests list if no attending guests are found, if ?attending_status=True """
        # All test guests have attending=False by default
        response = client.get(
            f'{reverse("api:attending_guests")}?attending_status=True',
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(guests, [])

    def test_attending_status_true_returns_attending_guests(self):
        """ Confirm we only return attending guests, if ?attending_status=True """
        # Update guest_2 to attending=True
        self.guest_2.attending = True
        self.guest_2.save()
        response = client.get(
            f'{reverse("api:attending_guests")}?attending_status=True',
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(len(guests), 1)
        self.assertEqual(guests[0].get('guest_uuid'), str(self.guest_2.guest_uuid))

    #                                                                                                      Not attending
    def test_attending_status_false_invitation_responded_false_returns_empty_guests_list(self):
        """
        Confirm we return an empty guests list if invitation hasn't been responded to, if no attending_status param
        """
        # Update invitation to responded=False, all guests already have attending=False
        self.invitation.responded = False
        self.invitation.save()
        response = client.get(
            reverse('api:attending_guests'),
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(guests, [])

    def test_attending_status_false_no_results_returns_empty_guests_list(self):
        """ Confirm we return an empty guests list if no attending guests are found, if no attending_status param """
        # Updating all guests to attending=True
        self.invitation_guests.update(attending=True)
        response = client.get(
            reverse('api:attending_guests'),
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(guests, [])

    def test_attending_status_false_returns_not_attending_guests(self):
        """ Confirm we only return guests who are not attending, if no attending_status param """
        # Update guest_2 to attending=True
        self.guest_2.attending = True
        self.guest_2.save()
        response = client.get(
            reverse('api:attending_guests'),
            content_type='application/json',
        )
        response_json = response.json()
        guests = response_json.get('guests', [])
        self.assertEqual(len(guests), 1)
        self.assertEqual(guests[0].get('guest_uuid'), str(self.guest_1.guest_uuid))


class RespondedInvitationsTest(TestCase):
    """ Test suite for responded_invitations view """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.invitations = seed_invitations(invitation_count=2)
        cls.invitation_1 = cls.invitations.first()
        cls.invitation_2 = cls.invitations.last()

    #                                                                                                      Generic tests
    def test_success(self):
        """ Confirm we return a 200 status code on success """
        response = client.get(
            reverse('api:responded_invitations'),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_success_returns_correct_invitations_data(self):
        """ Confirm we return the correct invitations serialized data in the response """
        response = client.get(
            reverse('api:responded_invitations'),
            content_type='application/json',
        )
        response_json = response.json()
        invitations = response_json.get('invitations', [])
        invitation_fields = InvitationSerializer.Meta.fields
        for invitation in invitations:
            # Check the invitation fields
            for invitation_field in invitation_fields:
                self.assertIn(invitation_field, invitation)
            # Check the guest fields
            guests = invitation.get('guests', [])
            guest_fields = GuestSerializer.Meta.fields
            for guest in guests:
                for guest_field in guest_fields:
                    self.assertIn(guest_field, guest)

    #                                                                                                          Responded
    def test_responded_status_true_no_results_returns_empty_invitations_list(self):
        """
        Confirm we return an empty invitations list if no responded invitations are found, if ?responded_status=True
        """
        # All test invitations have attending=False by default
        response = client.get(
            f'{reverse("api:responded_invitations")}?responded_status=True',
            content_type='application/json',
        )
        response_json = response.json()
        invitations = response_json.get('invitations', [])
        self.assertEqual(invitations, [])

    def test_responded_status_true_returns_attending_invitations(self):
        """ Confirm we only return responded invitations, if ?responded_status=True """
        # Update invitation_1 to responded=True
        self.invitation_1.responded = True
        self.invitation_1.save()
        response = client.get(
            f'{reverse("api:responded_invitations")}?responded_status=True',
            content_type='application/json',
        )
        response_json = response.json()
        invitations = response_json.get('invitations', [])
        self.assertEqual(len(invitations), 1)
        self.assertEqual(invitations[0].get('invitation_uuid'), str(self.invitation_1.invitation_uuid))

    #                                                                                                   Pending response
    def test_responded_status_false_no_results_returns_empty_invitations_list(self):
        """
        Confirm we return an empty invitations list if no invitations pending response are found,
        if no responded_status param
        """
        # Update all invitations to responded=True
        self.invitations.update(responded=True)
        response = client.get(
            reverse("api:responded_invitations"),
            content_type='application/json',
        )
        response_json = response.json()
        invitations = response_json.get('invitations', [])
        self.assertEqual(invitations, [])

    def test_responded_status_false_returns_pending_response_invitations(self):
        """ Confirm we only return invitations pending response, if no responded_status param """
        # Update invitation_1 to responded=True
        self.invitation_1.responded = True
        self.invitation_1.save()
        response = client.get(
            reverse("api:responded_invitations"),
            content_type='application/json',
        )
        response_json = response.json()
        invitations = response_json.get('invitations', [])
        self.assertEqual(len(invitations), 1)
        self.assertEqual(invitations[0].get('invitation_uuid'), str(self.invitation_2.invitation_uuid))
