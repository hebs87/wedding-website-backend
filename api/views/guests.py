from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from guests.models import Invitation
from api.serializers import InvitationSerializer
from api.views.accounts import error_message


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def invitation(request, **kwargs):
    """
    GET - Return the invitation details, with associated guests
    POST - Allow user to respond to the invitation, and confirm the attendance and song for each guest
    """
    code = kwargs.get('code', '')
    data = request.data
    temp_invitation = Invitation()
    success_data = {'success': True}

    matching_invitation = temp_invitation.get_invitation(code=code)
    if not matching_invitation:
        return error_message(message='Sorry, we can\'t find an invitation with that code')

    if request.method == 'POST':
        success, error = matching_invitation.process_invitation_response(data=data)
        if not success:
            return error_message(message=error)

    # Same response for GET and POST
    invitation_data = InvitationSerializer(matching_invitation).data
    success_data['invitation'] = invitation_data

    return Response(success_data, status=status.HTTP_200_OK)
