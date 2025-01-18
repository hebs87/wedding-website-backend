from rest_framework import status
from rest_framework.response import Response


def is_active_admin(func):
    """
    Function to confirm user is active admin
    """
    def inner(request, *args, **kwargs):
        user = request.user

        # Confirm user is active user
        if not user.role == 'admin' or not user.is_active:
            data = {
                'success': False,
                'error_message': 'You must be an admin to access this'
            }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

        return func(request, *args, **kwargs)
    return inner
