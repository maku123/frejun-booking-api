from django.urls import path
from .views import AvailableRoomsView, BookingListCreateView, BookingCancelView

urlpatterns = [
    path('rooms/available/', AvailableRoomsView.as_view(), name='available-rooms'),
    path('bookings/', BookingListCreateView.as_view(), name='create-booking'),
    path('cancel/<uuid:booking_id>/', BookingCancelView.as_view(), name='cancel-booking'),
]