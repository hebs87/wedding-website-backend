import random
import string
import base64
import boto3

from django.conf import settings
from django.core.files.base import ContentFile

from data.constants import RANDOM_STRING_LENGTH


def generate_random_string(length=RANDOM_STRING_LENGTH):
    """ Generate a random alphanumeric string of a specified length """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()


def convert_base_64_string_to_file(base64_string, filename):
    """ Convert a base 64 string to a Django-savable file format """
    # Get the format, string and extension
    file_format, file_string = base64_string.split(';base64,')
    name = filename
    data = ContentFile(base64.b64decode(file_string), name=name)

    return data


def delete_test_files():
    """ Delete all test files on TearDown in test suites """

    # Initiate the S3 client
    s3_client = boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    bucket = s3_client.Bucket(bucket_name)

    objects_to_delete = []
    objects = bucket.objects.filter(Prefix=f'memories/test/')
    objects_to_delete.extend(
        [{'Key': o.key} for o in objects]
    )

    if len(objects_to_delete):
        s3_client.meta.client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
