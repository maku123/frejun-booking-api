import uuid
from django.db import models
from django.contrib.auth.models import User

# Choices for Gender
class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'

# New UserProfile Model
class UserProfile(models.Model):
    """
    Extends the built-in User model to include age and gender.
    """
    # This creates the one-to-one link. If a User is deleted, their profile is too.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=Gender.choices)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Let's define choices for Room Types to ensure data consistency.
# This prevents typos like 'private' vs 'Private'.
class RoomType(models.TextChoices):
    PRIVATE = 'PRIVATE', 'Private Room'
    CONFERENCE = 'CONFERENCE', 'Conference Room'
    SHARED = 'SHARED', 'Shared Desk'

class Room(models.Model):
    """
    Represents a workspace room.
    """
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

class Team(models.Model):
    """
    Represents a team of users.
    """
    name = models.CharField(max_length=100)
    # A ManyToManyField allows a User to be in multiple Teams,
    # and a Team to have multiple Users.
    members = models.ManyToManyField(User, related_name='teams')

    def __str__(self):
        return self.name

class Booking(models.Model):
    """
    Represents a booking for a room by a user or a team.
    """
    # We use a UUID for the booking ID to ensure it's unique across systems.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ForeignKey creates a many-to-one relationship.
    # Many bookings can belong to one room.
    # on_delete=models.CASCADE means if a Room is deleted, all its bookings are also deleted.
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    
    # The user who created the booking.
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # A booking can be for a team. This is optional (nullable).
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.room.name} from {self.start_time} to {self.end_time}"

    class Meta:
        # This ensures that we can't have two bookings for the same room at the exact same start time.
        # The true overlap logic will be handled in the API logic layer.
        unique_together = ('room', 'start_time',)
        ordering = ['start_time']