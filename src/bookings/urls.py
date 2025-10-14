from django.urls import path
from .views import AvailableRoomsView

urlpatterns = [
    path('rooms/available/', AvailableRoomsView.as_view(), name='available-rooms'),
]