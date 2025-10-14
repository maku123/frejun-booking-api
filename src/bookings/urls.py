from django.urls import path
from .views import AvailableRoomsView, BookingListCreateView

urlpatterns = [
    path('rooms/available/', AvailableRoomsView.as_view(), name='available-rooms'),
    path('bookings/', BookingListCreateView.as_view(), name='create-booking'),
]