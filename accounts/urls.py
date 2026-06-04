from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Passenger endpoints
    path("register/", views.register_passenger, name="register_passenger"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    path("passenger_login/", views.passenger_login, name="passenger_login"),

    # Driver endpoints
    path("register_driver/", views.register_driver, name="register_driver"),
    path("driver_login/", views.driver_login, name="driver_login"),
    path("drivers/", views.list_drivers, name="list_drivers"),
    path("verify_driver/<int:driver_id>/", views.verify_driver, name="verify_driver"),
    path("unverify_driver/<int:driver_id>/", views.unverify_driver, name="unverify_driver"),

    # Ride endpoints
    path("request_ride/", views.request_ride, name="request_ride"),
    path("assign_driver/", views.assign_driver, name="assign_driver"),
    path("pending_rides/", views.pending_rides, name="pending_rides"),
    path("accept_ride/<int:ride_id>/", views.accept_ride, name="accept_ride"),
    path("complete_ride/", views.complete_ride, name="complete_ride"),

    # Ride history endpoints
    path("driver_rides/", views.driver_rides, name="driver_rides"),
    path("passenger_rides/", views.passenger_rides, name="passenger_rides"),
    path("rate_driver/", views.rate_driver, name="rate_driver"),

    # JWT authentication endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
