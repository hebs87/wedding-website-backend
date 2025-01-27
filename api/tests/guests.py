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

    def test_party_only(self):
        """ Confirm we return the 'party_only' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('party_only', ''), self.guest.party_only)

    def test_wedding(self):
        """ Confirm we return the 'wedding' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('wedding', ''), self.guest.wedding)

    def test_party(self):
        """ Confirm we return the 'party' field """
        serializer = GuestSerializer(self.guest).data
        self.assertEqual(serializer.get('party', ''), self.guest.party)


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

    def test_invitation_type(self):
        """ Confirm we return the 'invitation_type' field """
        serializer = InvitationSerializer(self.invitation).data
        guests = self.invitation.guests.all()
        invitation_type = 'party' if all(guest.party_only for guest in guests) else 'wedding'
        self.assertEqual(serializer.get('invitation_type', ''), invitation_type)

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
            elif field == 'invitation_uuid':
                self.assertEqual(invitation.get(field, ''), str(getattr(self.invitation_1, field)))
            elif field == 'invitation_type':
                invitation_type = 'party' if all(guest.party_only for guest in self.invitation_1_guests) else 'wedding'
                self.assertEqual(invitation.get(field, ''), invitation_type)
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
            'wedding': True,
            'party': True,
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
        excluded_fields = ['guest_uuid', 'party_only']
        fields = [field for field in GuestSerializer.Meta.fields if field not in excluded_fields]
        for index, guest in enumerate(self.invitation_1.guests.all()):
            guest_data = guests_data[index]
            guest.refresh_from_db()
            for field in fields:
                self.assertEqual(getattr(guest, field), guest_data.get(field, ''))

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
