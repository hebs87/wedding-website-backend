from django.test import TestCase
from django.core.files.base import ContentFile
from django.conf import settings

from .helpers import generate_random_string, convert_base_64_string_to_file
from data.constants import RANDOM_STRING_LENGTH


class GenerateRandomStringTest(TestCase):
    """ Test module for generate_random_string helper method """

    def test_generate_random_string_default(self):
        """ Confirm we return an alphanumeric string, same length as RANDOM_STRING_LENGTH, by default """
        random_string = generate_random_string()
        self.assertEqual(len(random_string), RANDOM_STRING_LENGTH)
        self.assertTrue(random_string.isalnum())

    def test_generate_random_string_custom_length(self):
        """ Confirm we return an alphanumeric string by of custom length when we specify length arg """
        custom_length = 5
        random_string = generate_random_string(length=custom_length)
        self.assertEqual(len(random_string), custom_length)
        self.assertTrue(random_string.isalnum())


class ConvertBase64StringToFileHelperTest(TestCase):
    """ Test module for convert_base_64_string_to_file helper method """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.image = settings.TEST_BASE_64_IMAGE

    def test_convert_base_64_string_to_file_image_returns_correct_file_convert_extension_false(self):
        """ Confirm we return a file instance when passed a base 64 string gif image """
        data = convert_base_64_string_to_file(base64_string=self.image, filename='test-image.gif')
        self.assertIsInstance(data, ContentFile)
        self.assertEqual('test-image.gif', data.name)
