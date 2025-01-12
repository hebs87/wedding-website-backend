import uuid

from model_utils.models import TimeStampedModel

from django.db import models


# Create your models here.
class Picture(TimeStampedModel):
    """
    Picture model to allow uploading a picture
    """
    picture_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.ImageField(upload_to='memories/', blank=False)
