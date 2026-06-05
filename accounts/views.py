import random
import json
from math import radians, sin, cos, sqrt, atan2

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Passenger, Driver, Ride
from accounts.serializers import PassengerSerializer, DriverSerializer, RideSerializer

User = get_user_model()

# -----------------------------
# Utility: Price Calculation
# -----------------------------
def calculate_price(lat1, lng1, lat2, lng2, rate_per_km=5):
    try:
        if not lat1 or not lng1 or not lat2 or not lng2:
            return 0
        R = 6371
        dlat = radians(float(lat2) - float(lat1))
        dlng = radians(float(lng2) - float(lng1))
        a = sin(dlat/2)**2 + cos(radians(float(lat1))) * cos(radians(float(lat2))) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        return round(distance * rate_per_km, 2)
    except Exception:
        return 0

# -----------------------------
# Passenger Registration
# -----------------------------
@csrf_exempt
def register_passenger(request):
    try:
        if request.method != "POST":
            return JsonResponse(
                {"status": False, "message": "Invalid method"},
                status=405
            )

        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": "Invalid JSON",
                "error": str(e)
            }, status=400)

        name = data.get("name")
        phone = data.get("phone")

        if not name or not phone:
            return JsonResponse({
                "status": False,
                "message": "Name and phone required"
            }, status=400)

        otp = str(random.randint(100000, 999999))

        user, user_created = User.objects.get_or_create(
            username=phone,
            defaults={
                "first_name": name
            }
        )

        passenger, passenger_created = Passenger.objects.get_or_create(
            phone=phone,
            defaults={
                "name": name,
                "otp": otp,
                "verified": False,
                "user": user
            }
        )

        if not passenger_created:
            passenger.name = name
            passenger.otp = otp
            passenger.verified = False
            passenger.user = user
            passenger.save()

        return JsonResponse({
            "status": True,
            "message": "Registration successful",
            "passenger_id": passenger.id,
            "otp": otp,
            "user_created": user_created,
            "passenger_created": passenger_created
        })

    except Exception as e:
        import traceback

        return JsonResponse({
            "status": False,
            "error_type": type(e).__name__,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)
# -----------------------------
# Verify OTP + JWT
# -----------------------------
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid JSON"}, status=400)

        phone = data.get("phone")
        otp = data.get("otp")

        if not phone or not otp:
            return JsonResponse({"status": False, "message": "Missing phone or otp"}, status=400)

        try:
            passenger = Passenger.objects.get(phone=phone, otp=otp)
            passenger.verified = True
            passenger.save()

            refresh = RefreshToken.for_user(passenger.user)
            return JsonResponse({
                "status": True,
                "message": "OTP verified",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })
        except Passenger.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invalid phone or otp"}, status=401)
    return JsonResponse({"status": False, "message": "Invalid method"}, status=405)

# -----------------------------
# Passenger Login
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def passenger_login(request):
    phone = request.data.get("phone")

    if not phone:
        return Response({"status": False, "message": "Phone is required"}, status=400)

    try:
        passenger = Passenger.objects.get(phone=phone)
        if not passenger.verified:
            return Response({"status": False, "message": "Passenger not verified"}, status=401)

        refresh = RefreshToken.for_user(passenger.user)
        return Response({
            "status": True,
            "message": "Login successful",
            "passenger_id": passenger.id,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
    except Passenger.DoesNotExist:
        return Response({"status": False, "message": "Passenger not found"}, status=401)

# -----------------------------
# Driver Registration
# -----------------------------
@csrf_exempt
def register_driver(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid JSON"}, status=400)

        full_name = data.get("full_name")
        phone = data.get("phone")
        license_number = data.get("license_number")
        car_model = data.get("car_model")
        car_plate = data.get("car_plate")

        if not full_name or not phone:
            return JsonResponse({"status": False, "message": "Full name and phone required"}, status=400)

        user, _ = User.objects.get_or_create(
            username=phone,
            defaults={"first_name": full_name}
        )

        driver, created_driver = Driver.objects.get_or_create(
            user=user,
            defaults={
                "full_name": full_name,
                "phone": phone,
                "license_number": license_number,
                "car_model": car_model,
                "car_plate": car_plate,
                "is_verified": False
            }
        )

        if not created_driver:
            driver.full_name = full_name
            driver.license_number = license_number
            driver.car_model = car_model
            driver.car_plate = car_plate
            driver.is_verified = False
            driver.save()

        return JsonResponse({
            "status": True,
            "message": "Driver registration submitted",
            "driver_id": driver.id
        })
    return JsonResponse({"status": False, "message": "Invalid method"}, status=405)

# -----------------------------
# Driver Login
# -----------------------------
@csrf_exempt
def driver_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"status": False, "message": "Invalid JSON"}, status=400)

        phone = data.get("phone")
        license_number = data.get("license_number")

        if not phone or not license_number:
            return JsonResponse({"status": False, "message": "Phone and license required"}, status=400)

        try:
            driver = Driver.objects.get(phone=phone, license_number=license_number)
            if driver.is_verified:
                refresh = RefreshToken.for_user(driver.user)
                return JsonResponse({
                    "status": True,
                    "message": "Login successful",
                    "driver_id": driver.id,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                })
            else:
                return JsonResponse({"status": False, "message": "Driver not verified"}, status=403)
        except Driver.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invalid credentials"}, status=401)
    return JsonResponse({"status": False, "message": "Invalid method"}, status=405)

# -----------------------------
# Request Ride (Passenger)
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_ride(request):
    passenger = Passenger.objects.get(user=request.user)
    data = request.data

    pickup_location = data.get("pickup_location")
    dropoff_location = data.get("dropoff_location")
    pickup_lat = data.get("pickup_lat")
    pickup_lng = data.get("pickup_lng")
    dropoff_lat = data.get("dropoff_lat")
    dropoff_lng = data.get("dropoff_lng")

    if not pickup_location or not dropoff_location:
        return Response({"status": False, "message": "Pickup and dropoff required"}, status=400)

    if not pickup_lat or not pickup_lng or not dropoff_lat or not dropoff_lng:
        return Response({"status": False, "message": "Coordinates required"}, status=400)

    price = calculate_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    if price <= 0:
        return Response({"status": False, "message": "Invalid price calculation"}, status=400)

    ride = Ride.objects.create(
        passenger=passenger,
        pickup_location=pickup_location,
        dropoff_location=dropoff_location,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        price=price,
        status="pending"
    )

    serializer = RideSerializer(ride)
    return Response({"status": True, "message": "Ride requested", "ride": serializer.data}, status=201)
# -----------------------------
# List Drivers (Passenger)
# -----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_drivers(request):
    drivers = Driver.objects.filter(is_verified=True)
    serializer = DriverSerializer(drivers, many=True)
    return Response({"status": True, "drivers": serializer.data})

# -----------------------------
# Assign Driver (Passenger)
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_driver(request):
    driver_id = request.data.get("driverId")
    ride_id = request.data.get("rideId")

    if not driver_id or not ride_id:
        return Response({"status": False, "message": "Missing driverId or rideId"}, status=400)

    try:
        driver = Driver.objects.get(id=driver_id, is_verified=True)
        ride = Ride.objects.get(id=ride_id, passenger__user=request.user)

        ride.driver = driver
        ride.save()

        serializer = RideSerializer(ride)
        return Response({"status": True, "message": "Driver assigned", "ride": serializer.data})
    except Driver.DoesNotExist:
        return Response({"status": False, "message": "Driver not found"}, status=404)
    except Ride.DoesNotExist:
        return Response({"status": False, "message": "Ride not found"}, status=404)

# -----------------------------
# Pending Rides (Driver)
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_rides(request):
    rides = Ride.objects.filter(status="pending")
    serializer = RideSerializer(rides, many=True)
    return Response({"status": True, "rides": serializer.data})

# -----------------------------
# Accept Ride (Driver)
# -----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_ride(request, ride_id):
    try:
        driver = Driver.objects.get(user=request.user, is_verified=True)
    except Driver.DoesNotExist:
        return Response({"status": False, "message": "Driver not found or not verified"}, status=400)

    try:
        ride = Ride.objects.get(id=ride_id, status="pending")
    except Ride.DoesNotExist:
        return Response({"status": False, "message": "Ride not found or already accepted"}, status=404)

    ride.driver = driver
    ride.status = "accepted"
    ride.save()

    serializer = RideSerializer(ride)
    return Response({"status": True, "message": "Ride accepted", "ride": serializer.data})

# -----------------------------
# Complete Ride (Driver)
# -----------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_ride(request):
    ride_id = request.data.get("ride_id")

    try:
        driver = Driver.objects.get(user=request.user, is_verified=True)
    except Driver.DoesNotExist:
        return Response({"status": False, "message": "Driver not found or not verified"}, status=400)

    try:
        ride = Ride.objects.get(id=ride_id, driver=driver, status="accepted")
    except Ride.DoesNotExist:
        return Response({"status": False, "message": "Ride not found or not accepted"}, status=400)

    ride.status = "completed"
    ride.save()

    serializer = RideSerializer(ride)
    return Response({"status": True, "message": "Ride completed", "ride": serializer.data})

# -----------------------------
# Passenger Ride History
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def passenger_rides(request):
    passenger = Passenger.objects.get(user=request.user, verified=True)
    rides = Ride.objects.filter(passenger=passenger)
    serializer = RideSerializer(rides, many=True)
    return Response({"status": True, "rides": serializer.data})

# -----------------------------
# Driver Ride History
# -----------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def driver_rides(request):
    driver = Driver.objects.get(user=request.user, is_verified=True)
    rides = Ride.objects.filter(driver=driver)
    serializer = RideSerializer(rides, many=True)
    return Response({"status": True, "rides": serializer.data})

# -----------------------------
# Rate Driver (Passenger)
# -----------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_driver(request):
    ride_id = request.data.get("ride_id")
    rating = request.data.get("rating")

    if rating is None or not (0 <= int(rating) <= 5):
        return Response({"status": False, "message": "Rating must be between 0 and 5"}, status=400)

    passenger = Passenger.objects.get(user=request.user, verified=True)

    try:
        ride = Ride.objects.get(id=ride_id, passenger=passenger, status="completed")
    except Ride.DoesNotExist:
        return Response({"status": False, "message": "Ride not found or not completed"}, status=400)

    ride.rating = int(rating)
    ride.save()

    serializer = RideSerializer(ride)
    return Response({"status": True, "message": "Driver rated", "ride": serializer.data})
