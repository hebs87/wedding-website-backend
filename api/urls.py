from django.urls import path

from .views import invitation, pictures


app_name = 'api'

urlpatterns = [
    # guests views
    path('invitation/<str:code>', invitation, name='invitation'),

    # memories views
    path('pictures/<str:code>', pictures, name='pictures'),
]
