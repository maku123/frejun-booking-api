from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Room, RoomType, User, Team, Booking
from datetime import datetime, timedelta
from django.utils import timezone

class BookingAPITests(APITestCase):
    """
    Test suite for the Booking API.
    """

    def setUp(self):
        """
        Set up the initial state for each test.
        This method is run before every single test function.
        """
        # Clear all existing models to ensure a clean slate
        Room.objects.all().delete()
        User.objects.all().delete()
        Team.objects.all().delete()
        Booking.objects.all().delete()

        # Create predictable objects for our tests
        self.private_room = Room.objects.create(name="Test Private Room", room_type=RoomType.PRIVATE, capacity=1)
        self.conference_room = Room.objects.create(name="Test Conference Room", room_type=RoomType.CONFERENCE, capacity=10)

        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')

        self.large_team = Team.objects.create(name="Large Team")
        self.large_team.members.add(self.user1, self.user2, self.user3)

        self.small_team = Team.objects.create(name="Small Team")
        self.small_team.members.add(self.user1)
        
        # We need to log in a user to perform POST requests in some setups
        self.client.force_authenticate(user=self.user1)
        
        # Use timezone.now() to create timezone-aware datetime objects.
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=1)


    def test_get_available_rooms_success(self):
        """
        Ensure we can successfully get a list of available rooms.
        """
        start_str = self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = self.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = reverse('available-rooms') + f'?start_time={start_str}&end_time={end_str}'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


    def test_create_individual_booking_success(self):
        """
        Ensure an individual can successfully book a private room.
        """
        url = reverse('list-create-booking')
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "booking_type": "individual"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.first().room, self.private_room)


    def test_create_team_booking_success(self):
        """
        Ensure a team with >= 3 members can book a conference room.
        """
        url = reverse('list-create-booking')
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "booking_type": "team",
            "team_id": self.large_team.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.first().room, self.conference_room)


    def test_create_team_booking_fails_with_small_team(self):
        """
        Ensure a team with < 3 members cannot book a conference room.
        """
        url = reverse('list-create-booking')
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "booking_type": "team",
            "team_id": self.small_team.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 0) # Assert no booking was created


    def test_booking_fails_when_no_rooms_available(self):
        """
        Ensure the API returns an error if no suitable rooms are available.
        """
        # First, book the only private room
        Booking.objects.create(
            room=self.private_room,
            booked_by=self.user1,
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        # Now, try to book another individual room at the same time
        url = reverse('list-create-booking')
        data = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "booking_type": "individual"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # We should still only have the one booking we created manually
        self.assertEqual(Booking.objects.count(), 1)