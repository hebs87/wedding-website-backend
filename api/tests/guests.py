from django.test import TestCase, Client
from django.urls import reverse

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
        """ Confirm we return the 'test_guests' field """
        serializer = InvitationSerializer(self.invitation).data
        guests = serializer.get('guests', [])
        self.assertTrue(len(guests))
        for index, guest in enumerate(guests):
            self.assertEqual(guest.get('guest_uuid', ''), str(self.guests[index].guest_uuid))
            self.assertEqual(guest.get('name', ''), self.guests[index].name)
            self.assertEqual(guest.get('attending', ''), self.guests[index].attending)
            self.assertEqual(guest.get('song', ''), self.guests[index].song)
            self.assertEqual(guest.get('meal', ''), self.guests[index].meal)


#                                              -- VIEW TESTS --
class InvitationTest(TestCase):
    """ Test suite for invitation view """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations()
        cls.invitation = invitations.first()
        cls.guests = cls.invitation.guests.all()
        cls.failure_kwargs = {'code': 'invalid_code'}
        cls.success_kwargs = {'code': cls.invitation.code}

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
        self.assertEqual('', response_json.get('Sorry, we can\'t find an invitation with that code.', ''))

    #                                                                                                     Get invitation
    def test_success_returns_invitation_data(self):
        """ Confirm we return the invitation data, including guests, on success """
        response = client.get(
            reverse('api:invitation', kwargs=self.success_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        invitation = response_json.get('invitation', {})
        guests = invitation.get('guests', [])
        # Check main invitation data
        self.assertEqual(invitation.get('invitation_uuid', ''), str(self.invitation.invitation_uuid))
        self.assertEqual(invitation.get('name', ''), self.invitation.name)
        self.assertEqual(invitation.get('responded', ''), self.invitation.responded)
        self.assertEqual(invitation.get('additional_info', ''), self.invitation.additional_info)
        # Check guest data
        self.assertTrue(len(guests))
        for index, guest in enumerate(guests):
            self.assertEqual(guest.get('guest_uuid', ''), str(self.guests[index].guest_uuid))
            self.assertEqual(guest.get('name', ''), self.guests[index].name)
            self.assertEqual(guest.get('attending', ''), self.guests[index].attending)
            self.assertEqual(guest.get('song', ''), self.guests[index].song)
            self.assertEqual(guest.get('meal', ''), self.guests[index].meal)

    #                                                                                              Respond to invitation
