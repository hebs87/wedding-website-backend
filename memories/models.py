import uuid

from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.helpers import generate_random_string, convert_base_64_string_to_file


# Create your models here.
class Picture(TimeStampedModel):
    """
    Picture model to allow uploading a picture
    """
    picture_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.ImageField(upload_to='memories/', blank=False)
    approved = models.BooleanField(default=False)

    @staticmethod
    def get_pictures():
        """ Return all Picture instances, ordered by oldest to newest """
        return Picture.objects.all().order_by('created')

    @staticmethod
    def create_pictures(picture_files):
        """ Create Picture instances from a list of picture files """
        pictures, picture_uuids, has_errors, error = [], [], False, 'Please upload at least one picture'
        if not picture_files:
            return pictures, error

        for picture in picture_files:
            try:
                unique_string = generate_random_string()
                original_filename = picture.get('name', 'new-file')
                ext = original_filename.split('.')[-1]
                filename_without_ext = original_filename.replace(f'.{ext}', '')
                filename = f'{filename_without_ext}-{unique_string}.{ext}'
                file = picture.get('fileSrc', '')
                if settings.TESTING:
                    filename = f'test/{filename}'
                picture_file = convert_base_64_string_to_file(base64_string=file, filename=filename)
                new_picture = Picture.objects.create(file=picture_file)
                picture_uuids.append(new_picture.picture_uuid)
            except:
                continue

        pictures = Picture.objects.filter(picture_uuid__in=picture_uuids).order_by('created')

        error = 'We were unable to upload on or more of your pictures, please try again' if has_errors else ''
        return pictures, error
