from datetime import date

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model

from rest_framework.response import Response

from accounts.decorators import is_active_admin


client = Client()


#                                   -- DECORATOR TESTS --
@is_active_admin
def dummy_active_admin_view(request):
    """ A dummy view with the is_active_admin decorator - enables testing is_active_admin decorator """
    return Response()


class IsActiveAdminDecoratorTest(TestCase):
    """ Test module for is_active_admin decorator """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        User = get_user_model()
        # Create admin
        cls.admin = User.objects.create(
            email='admin@admin.co.uk',
            username='admin@admin.co.uk',
        )
        # Create user
        cls.user = User.objects.create(
            email='user@user.co.uk',
            username='user@user.co.uk',
            role='user'
        )
        cls.factory = RequestFactory()

    def test_user(self):
        """ Confirm we return an error for 'user' users  """
        request = self.factory.get('/test-view')
        request.user = self.user
        response = dummy_active_admin_view(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data.get('error_message'), 'You must be an admin to access this')

    def test_inactive_user(self):
        """ Confirm we return an error for inactive 'admin' users """
        self.admin.is_active = False
        self.admin.save()
        request = self.factory.get('/test-view')
        request.user = self.admin
        response = dummy_active_admin_view(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data.get('error_message'), 'You must be an admin to access this')

    def test_admin_success(self):
        """ Confirm that the @is_active_buyer_admin decorator returns success for buyer_admin users  """
        # Default role is buyer_admin
        # Mock a request and call the dummy_company_view view
        request = self.factory.get('/test-view')
        request.user = self.admin
        response = dummy_active_admin_view(request)
        self.assertEqual(response.status_code, 200)


#                                   -- VIEW TESTS --
