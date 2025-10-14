from rest_framework import serializers
from .models import Room, Booking

class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer to represent the Room model.
    """
    # We use 'get_room_type_display' to show the human-readable
    # name (e.g., "Private Room") instead of the database value ("PRIVATE").
    room_type = serializers.CharField(source='get_room_type_display')

    class Meta:
        model = Room
        # These are the fields that will be included in the JSON output.
        fields = ['id', 'name', 'room_type', 'capacity']

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    """
    # We can nest serializers! Here, we're showing the full room details
    # and the username of the booker, not just their IDs.
    room = RoomSerializer(read_only=True)
    booked_by = serializers.CharField(source='booked_by.username', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'room', 'booked_by', 'start_time', 'end_time']