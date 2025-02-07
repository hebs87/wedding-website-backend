from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from memories.models import Picture
from api.serializers import PictureSerializer
from utils.helpers import delete_test_files

client = Client()


#                                              -- SERIALIZER TESTS --
class PictureSerializerTest(TestCase):
    """ Test suite for PictureSerializer """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.pictures = [
            {
                'fileSrc': settings.TEST_BASE_64_IMAGE,
                'name': f'picture.gif',
            }
        ]
        temp_picture = Picture()
        pictures = temp_picture.create_pictures(picture_files=cls.pictures)[0]
        cls.picture = pictures.first()

    @classmethod
    def tearDownClass(cls):
        """ Custom teardown to delete temp files created in tests """
        # For deleting S3 bucket files
        delete_test_files()

        super().tearDownClass()

    def test_picture_uuid(self):
        """ Confirm we return the 'picture_uuid' field """
        serializer = PictureSerializer(self.picture).data
        self.assertEqual(serializer.get('picture_uuid', ''), str(self.picture.picture_uuid))

    def test_url(self):
        """ Confirm we return the 'url' field """
        serializer = PictureSerializer(self.picture).data
        self.assertEqual(serializer.get('url', ''), self.picture.file.url)

    def test_url_is_s3_url(self):
        """ Confirm the 'url' field is an S3 URL """
        serializer = PictureSerializer(self.picture).data
        picture_name = self.pictures[0].get('name', '').split('.')[0]
        # Remove the .gif from the file name to prevent error with random string appended to filename on creation
        url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/memories/test/{picture_name}'
        self.assertIn(url, serializer.get('url', ''))


#                                              -- VIEW TESTS --
class PicturesTest(TestCase):
    """ Test suite for pictures view """

    @classmethod
    def setUpTestData(cls):
        """ Initialise test data """
        cls.temp_picture = Picture()
        pictures = []
        for i in range(5):
            picture = {
                'fileSrc': settings.TEST_BASE_64_IMAGE,
                'name': f'picture-{i}.gif',
            }
            pictures.append(picture)
        cls.valid_kwargs = {'code': settings.GALLERY_CODE}
        cls.invalid_kwargs = {'code': 'invalid_code'}
        cls.data = {'pictures': pictures}

    @classmethod
    def tearDownClass(cls):
        """ Custom teardown to delete temp files created in tests """
        # For deleting S3 bucket files
        delete_test_files()

        super().tearDownClass()

    #                                                                                                      Generic tests
    def test_invalid_code_returns_error(self):
        """ Confirm we return an error if the code is invalid """
        response = client.get(
            reverse('api:pictures', kwargs=self.invalid_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json.get('error_message', ''), 'Sorry, that code isn\'t valid')

    def test_success(self):
        """ Confirm we return a 200 status code on success """
        response = client.get(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    #                                                                                                       Get pictures
    def test_get_pictures_no_pictures_returns_empty_list(self):
        """ Confirm we return an empty list if there are no Picture instances """
        response = client.get(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        pictures = response_json.get('pictures', [])
        self.assertEqual(pictures, [])

    def test_get_pictures_success_returns_correct_data(self):
        """ Confirm we return a list of all pictures in the correct order (oldest to newest) on success """
        self.temp_picture.create_pictures(picture_files=self.data.get('pictures', []))
        response = client.get(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
        )
        response_json = response.json()
        pictures = response_json.get('pictures', [])
        expected_pictures = Picture.objects.all().order_by('created')
        self.assertEqual(len(pictures), expected_pictures.count())
        fields = PictureSerializer.Meta.fields
        for index, picture in enumerate(pictures):
            for field in fields:
                self.assertIn(field, picture)
                if field == 'picture_uuid':
                    self.assertEqual(picture.get(field, ''), str(expected_pictures[index].picture_uuid))
                else:
                    picture_name = self.data.get('pictures', [])[index].get('name', '').split('.')[0]
                    url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/memories/test/{picture_name}'
                    self.assertIn(url, picture.get('url', ''))

    #                                                                                                    Upload pictures
    def test_upload_pictures_empty_pictures_list_returns_error(self):
        """ Confirm we return an empty list and error message when passed an empty list """
        self.data['pictures'] = []
        response = client.post(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        pictures = response_json.get('pictures', [])
        error = response_json.get('error_message', '')
        self.assertEqual(pictures, [])
        self.assertEqual(error, 'Please upload at least one picture')

    def test_upload_pictures_success_creates_and_returns_correct_data(self):
        """ Confirm we create and return a list of the created pictures on success """
        self.assertFalse(Picture.objects.exists())
        response = client.post(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        pictures = response_json.get('pictures', [])
        self.assertEqual(len(pictures), len(self.data.get('pictures', [])))
        fields = PictureSerializer.Meta.fields
        for picture in pictures:
            for field in fields:
                self.assertIn(field, picture)

    def test_upload_pictures_uploads_pictures_to_s3_bucket(self):
        """ Confirm we upload pictures to S3 bucket on success """
        response = client.post(
            reverse('api:pictures', kwargs=self.valid_kwargs),
            content_type='application/json',
            data=self.data,
        )
        response_json = response.json()
        pictures = response_json.get('pictures', [])
        for index, picture in enumerate(pictures):
            # Remove the .gif from each file name to prevent error with random string appended to filename on creation
            picture_name = self.data.get('pictures', [])[index].get('name', '').split('.')[0]
            url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/memories/test/{picture_name}'
            self.assertIn(url, picture.get('url', ''))
