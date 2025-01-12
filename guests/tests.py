from django.test import TestCase

from data.seed_tests import seed_invitations
from data.constants import RANDOM_STRING_LENGTH


#                                              -- MODEL TESTS --
class InvitationTest(TestCase):
    """ Test module for Invitation model """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        invitations = seed_invitations()
        cls.invitation = invitations.first()

    #                                                                                                         save(self)
    def test_save_creates_alphanumeric_code(self):
        """ Test we create an alphanumeric code """
        self.assertTrue(self.invitation.code.isalnum())

    #                                                                                  generate_random_string(length=10)
    def test_generate_random_string_default(self):
        """ Confirm we return an alphanumeric string, same length as RANDOM_STRING_LENGTH, by default """
        random_string = self.invitation.generate_random_string()
        self.assertEqual(len(random_string), RANDOM_STRING_LENGTH)
        self.assertTrue(random_string.isalnum())

    def test_generate_random_string_custom_length(self):
        """ Confirm we return an alphanumeric string by of custom length when we specify length arg """
        custom_length = 5
        random_string = self.invitation.generate_random_string(length=custom_length)
        self.assertEqual(len(random_string), custom_length)
        self.assertTrue(random_string.isalnum())

    #                                                                                               get_invitation(code)
    def test_get_invitation_by_code_not_found_returns_none(self):
        """ Confirm we return None if an invitation with the specified code doesn't exist """
        invitation = self.invitation.get_invitation(code='invalid_code')
        self.assertIsNone(invitation)

    def test_get_invitation_by_code_returns_invitation(self):
        """ Confirm we return the matching invitation instance on success """
        invitation = self.invitation.get_invitation(code=self.invitation.code)
        self.assertEqual(invitation, self.invitation)
