from django.urls import path

from .views import invitation, attending_guests, responded_invitations


app_name = 'api'

urlpatterns = [
    # guests views
    path('invitation/<str:code>', invitation, name='invitation'),
    path('attending-guests', attending_guests, name='attending_guests'),
    path('responded-invitations', responded_invitations, name='responded_invitations'),
]
