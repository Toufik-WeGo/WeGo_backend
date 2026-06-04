from rest_framework import serializers
from .models import Passenger, Driver, Ride

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = [
            "id", "name", "phone", "verified",
            "current_lat", "current_lng"   # ✅ expose passenger location
        ]


class DriverSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id", "full_name", "phone", "license_number",
            "car_model", "car_plate", "is_verified",
            "driver_lat", "driver_lng",   # ✅ expose driver location
            "average_rating"
        ]


class RideSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)

    # ✅ expose driver name + car plate directly for passenger UI
    driver_name = serializers.CharField(source="driver.full_name", read_only=True)
    driver_car_plate = serializers.CharField(source="driver.car_plate", read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id",
            "pickup_location", "dropoff_location",
            "pickup_lat", "pickup_lng",
            "dropoff_lat", "dropoff_lng",   # ✅ expose ride coordinates
            "price",                        # ✅ expose ride price
            "requested_at", "status", "rating",
            "passenger", "driver",
            "driver_name", "driver_car_plate"  # ✅ added for passenger info
        ]
