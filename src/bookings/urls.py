from django.urls import path
from .views import AvailableRoomsView, BookingCreateView

urlpatterns = [
    path('rooms/available/', AvailableRoomsView.as_view(), name='available-rooms'),
    path('bookings/', BookingCreateView.as_view(), name='create-booking'),
]