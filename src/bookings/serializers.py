from rest_framework import serializers
from .models import Room, Booking, Team
from django.utils import timezone

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

class BookingCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new booking. Handles input validation.
    """
    # We define the fields we expect the user to send in the POST request.
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    
    # We'll use a ChoiceField to ensure the user sends either 'individual' or 'team'.
    booking_type = serializers.ChoiceField(choices=['individual', 'team'])
    
    # team_id is not required for individual bookings.
    team_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        """
        Perform custom validation on the incoming data.
        """
        start_time = data['start_time']
        end_time = data['end_time']

        # Rule 1: Start time must be before end time.
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        # Rule 2: Bookings cannot be in the past.
        if start_time < timezone.now():
            raise serializers.ValidationError("Booking time cannot be in the past.")

        # Rule 3: If booking for a team, team_id must be provided.
        if data['booking_type'] == 'team' and not data.get('team_id'):
            raise serializers.ValidationError("Team ID is required for a team booking.")

        # Rule 4: Check if the specified team actually exists.
        if data.get('team_id'):
            if not Team.objects.filter(id=data['team_id']).exists():
                raise serializers.ValidationError("Specified team does not exist.")

        return data