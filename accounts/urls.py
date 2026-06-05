from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Passenger routes
    # -----------------------------
    path("register_passenger/", views.register_passenger, name="register_passenger"),
    path("verify_otp/", views.verify_otp, name="verify_otp"),
    path("passenger_login/", views.passenger_login, name="passenger_login"),
    path("passenger_rides/", views.passenger_rides, name="passenger_rides"),
    path("rate_driver/", views.rate_driver, name="rate_driver"),

    # -----------------------------
    # Driver routes
    # -----------------------------
    path("register_driver/", views.register_driver, name="register_driver"),
    path("driver_login/", views.driver_login, name="driver_login"),
    path("driver_rides/", views.driver_rides, name="driver_rides"),
    path("list_drivers/", views.list_drivers, name="list_drivers"),

    # -----------------------------
    # Ride routes
    # -----------------------------
    path("request_ride/", views.request_ride, name="request_ride"),
    path("assign_driver/", views.assign_driver, name="assign_driver"),
    path("pending_rides/", views.pending_rides, name="pending_rides"),
    path("accept_ride/<int:ride_id>/", views.accept_ride, name="accept_ride"),
    path("complete_ride/", views.complete_ride, name="complete_ride"),
]
