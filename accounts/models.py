from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.conf import settings

class User(AbstractUser):
    pass


class Passenger(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    verified = models.BooleanField(default=False)

    # ✅ Passenger’s last known location (for driver navigation)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    license_number = models.CharField(max_length=50)
    car_model = models.CharField(max_length=100)
    car_plate = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)

    # ✅ Driver’s current location for live tracking
    driver_lat = models.FloatField(null=True, blank=True)
    driver_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def average_rating(self):
        """Calculate average rating from completed rides."""
        return (
            self.rides.filter(status="completed", rating__isnull=False)
            .aggregate(Avg("rating"))["rating__avg"]
            or 0
        )


class Ride(models.Model):
    passenger = models.ForeignKey("Passenger", on_delete=models.CASCADE)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)

    # ✅ Coordinate fields for map preview
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    dropoff_lat = models.FloatField(null=True, blank=True)
    dropoff_lng = models.FloatField(null=True, blank=True)

    # ✅ Price field
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    requested_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("completed", "Completed"),
        ],
        default="pending"
    )

    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Ride {self.id} - {self.passenger.name}"
