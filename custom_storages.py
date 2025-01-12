from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """ Custom MediaStorage class to point to the correct S3 bucket name """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME


class MediaStorage(S3Boto3Storage):
    """ Custom MediaStorage class to point to the correct S3 bucket name """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
