from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Booking
from .serializers import RoomSerializer
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction
from .models import Team, RoomType
from .serializers import BookingCreateSerializer, BookingSerializer

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

class BookingCreateView(APIView):
    """
    API view for creating a booking.
    """
    def post(self, request, *args, **kwargs):
        # For this test, we'll get or create a dummy user.
        # In a real app, this would be `request.user` from an authentication system.
        user, _ = User.objects.get_or_create(username='testuser')

        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        booking_type = validated_data['booking_type']
        team_id = validated_data.get('team_id')

        try:
            # Use a transaction to prevent race conditions.
            with transaction.atomic():
                # Find rooms that are already booked during the requested time.
                overlapping_bookings = Booking.objects.filter(
                    start_time__lt=end_time, end_time__gt=start_time
                ).select_for_update() # Lock these rows until the transaction is complete.

                booked_room_ids = overlapping_bookings.values_list('room_id', flat=True)

                available_rooms = Room.objects.exclude(id__in=booked_room_ids)
                
                target_room = None

                if booking_type == 'individual':
                    # Priority: Private -> Shared
                    target_room = available_rooms.filter(room_type=RoomType.PRIVATE).first()
                    if not target_room:
                        # Logic for shared desks will be more complex, for now we find one
                        target_room = available_rooms.filter(room_type=RoomType.SHARED).first()

                elif booking_type == 'team':
                    team = Team.objects.get(id=team_id)
                    if team.members.count() < 3:
                        return Response({"error": "Teams must have at least 3 members to book a conference room."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    target_room = available_rooms.filter(room_type=RoomType.CONFERENCE).first()

                if not target_room:
                    return Response({"error": "No available rooms for the selected criteria and time slot."}, status=status.HTTP_404_NOT_FOUND)

                # Create the booking
                booking = Booking.objects.create(
                    room=target_room,
                    booked_by=user,
                    team=Team.objects.get(id=team_id) if team_id else None,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Use the original BookingSerializer to format the successful response
                response_serializer = BookingSerializer(booking)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # A generic error handler in case something unexpected happens
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
