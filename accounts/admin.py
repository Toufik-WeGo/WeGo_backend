from django.contrib import admin
from .models import Passenger, Driver, Ride

# -----------------------------
# Passenger Admin
# -----------------------------
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "verified", "otp", "user")
    list_filter = ("verified",)
    search_fields = ("name", "phone", "user__username")


# -----------------------------
# Driver Admin
# -----------------------------
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "license_number",
        "car_model", "car_plate", "is_verified", "user"
    )
    list_filter = ("is_verified", "car_model")
    search_fields = ("full_name", "phone", "license_number", "car_plate", "user__username")


# -----------------------------
# Ride Admin
# -----------------------------
@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "passenger",
        "driver",
        "pickup_location",
        "dropoff_location",
        "price",          # ✅ show price in list view
        "status",
        "requested_at",
        "rating",
    )
    list_filter = ("status", "requested_at")
    search_fields = (
        "passenger__name",
        "driver__full_name",
        "pickup_location",
        "dropoff_location"
    )
