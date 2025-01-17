from django.conf import settings
from django.test import TestCase

from .models import Picture
from utils.helpers import delete_test_files


# Create your tests here.
class PictureTest(TestCase):
    """ Test suite for Invitation model """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.temp_picture = Picture()
        cls.pictures = []
        for i in range(5):
            picture = {
                'fileSrc': settings.TEST_BASE_64_IMAGE,
                'name': f'picture-{i}.gif',
            }
            cls.pictures.append(picture)

    @classmethod
    def tearDownClass(cls):
        """ Custom teardown to delete temp files created in tests """
        # For deleting S3 bucket files
        delete_test_files()

        super().tearDownClass()

    #                                                                                     create_pictures(picture_files)
    def test_create_pictures_empty_picture_files_list_returns_error(self):
        """ Confirm we return an empty list and error message when passed an empty list """
        pictures, error = self.temp_picture.create_pictures(picture_files=[])
        self.assertEqual(pictures, [])
        self.assertEqual(error, 'Please upload at least one picture')

    def test_create_pictures_creates_and_returns_created_pictures(self):
        """ Confirm we create and return a queryset of the created Picture instances on success """
        self.assertFalse(Picture.objects.exists())
        pictures, error = self.temp_picture.create_pictures(picture_files=self.pictures)
        self.assertEqual(pictures.count(), len(self.pictures))
        for picture in pictures:
            self.assertIsInstance(picture, Picture)

    def test_create_pictures_uploads_pictures_to_s3_bucket(self):
        """ Confirm we upload pictures to S3 bucket on success """
        pictures, error = self.temp_picture.create_pictures(picture_files=self.pictures)
        for index, picture in enumerate(pictures):
            # Remove the .gif from each file name to prevent error with random string appended to filename on creation
            picture_name = self.pictures[index].get('name', '').split('.')[0]
            url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/memories/test/{picture_name}'
            self.assertIn(url, picture.file.url)
