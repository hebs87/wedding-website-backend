from django.urls import path

from .views import invitation, attending_guests


app_name = 'api'

urlpatterns = [
    path('invitation/<str:code>', invitation, name='invitation'),
    path('attending-guests', attending_guests, name='attending_guests'),
]
