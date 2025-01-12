from django.urls import path

from .views import invitation


app_name = 'api'

urlpatterns = [
    path('invitation/<str:code>', invitation, name='invitation'),
]
