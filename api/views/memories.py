from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from memories.models import Picture
from api.serializers import PictureSerializer
from api.views.accounts import error_message


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def pictures(request):
    """
    GET - Return a list of all Picture instances
    POST - Allow user to upload a list of images
    """
    picture_files = request.data.get('pictures', [])
    temp_picture = Picture()
    success_data = {'success': True}

    if request.method == 'POST':
        uploaded_pictures, error = temp_picture.create_pictures(picture_files=picture_files)
        if error:
            return error_message(message=error)
    else:
        uploaded_pictures = temp_picture.get_pictures()

    # Same response for GET and POST
    uploaded_pictures_data = PictureSerializer(uploaded_pictures, many=True).data
    success_data['pictures'] = uploaded_pictures_data

    return Response(success_data, status=status.HTTP_200_OK)
