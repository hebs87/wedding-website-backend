from rest_framework.response import Response
from rest_framework import status


def error_message(message, request_status=status.HTTP_400_BAD_REQUEST):
    """
    A helper function to return a standard error response, and override the response status_code
    """
    data = {
        'success': False,
        'error_message': message,
    }

    return Response(data, status=request_status)
