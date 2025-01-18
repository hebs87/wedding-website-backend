from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from guests.models import Invitation, Guest
from api.serializers import InvitationSerializer, GuestSerializer
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


@api_view(['GET'])
@permission_classes((AllowAny,))
def attending_guests(request):
    """
    GET:
        - attending_status=True URL param - gets list of attending guests
        - No attending_status URL param - gets list of not attending guests
    """
    attending_status = bool(request.GET.get('attending_status', False))
    temp_guest = Guest()
    success_data = {'success': True}

    guests = temp_guest.attending_guests(attending_status=attending_status)
    guests_data = GuestSerializer(guests, many=True).data
    success_data['guests'] = guests_data

    return Response(success_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def responded_invitations(request):
    """
    GET:
        - responded_status=True URL param - gets list of responded invitations
        - No responded_status URL param - gets list of invitations pending response
    """
    responded_status = bool(request.GET.get('responded_status', False))
    temp_guest = Invitation()
    success_data = {'success': True}

    invitations = temp_guest.responded_invitations(responded_status=responded_status)
    invitations_data = InvitationSerializer(invitations, many=True).data
    success_data['invitations'] = invitations_data

    return Response(success_data, status=status.HTTP_200_OK)
