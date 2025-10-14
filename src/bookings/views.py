from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Booking
from .serializers import RoomSerializer
from django.db.models import Q
from datetime import datetime

class AvailableRoomsView(APIView):
    """
    API view to get available rooms for a given time slot.
    """
    def get(self, request, *args, **kwargs):
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')

        if not start_time_str or not end_time_str:
            return Response(
                {"error": "Both 'start_time' and 'end_time' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {"error": "Invalid datetime format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_time >= end_time:
            return Response(
                {"error": "Invalid time range. End time must be after start time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        overlapping_bookings = Booking.objects.filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )

        booked_room_ids = overlapping_bookings.values_list('room_id', flat=True)

        # Only exclude rooms if there are actually any bookings in the given slot.
        # Otherwise, the `NOT IN ()` SQL query will return an empty list.
        if booked_room_ids.exists():
            available_rooms = Room.objects.exclude(id__in=booked_room_ids)
        else:
            # If no rooms are booked, all rooms are available.
            available_rooms = Room.objects.all()

        serializer = RoomSerializer(available_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)