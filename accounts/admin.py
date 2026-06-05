from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Passenger, Driver, Ride

# -----------------------------
# Passenger Admin
# -----------------------------
@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "verified", "otp", "user")
    list_filter = ("verified",)
    ordering = ("name",)
    list_per_page = 20

    # ✅ Actions supplémentaires
    actions = ["mark_verified", "reset_otp"]

    def mark_verified(self, request, queryset):
        queryset.update(verified=True)
        self.message_user(request, _("Selected passengers marked as verified."))
    mark_verified.short_description = "Mark selected passengers as verified"

    def reset_otp(self, request, queryset):
        for passenger in queryset:
            passenger.otp = "000000"  # ou générer un OTP aléatoire
            passenger.save()
        self.message_user(request, _("OTP reset for selected passengers."))
    reset_otp.short_description = "Reset OTP for selected passengers"


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
    ordering = ("full_name",)
    list_per_page = 20

    # ✅ Actions supplémentaires
    actions = ["mark_verified", "unverify_driver"]

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, _("Selected drivers marked as verified."))
    mark_verified.short_description = "Mark selected drivers as verified"

    def unverify_driver(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, _("Selected drivers marked as unverified."))
    unverify_driver.short_description = "Unverify selected drivers"


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
        "price",
        "status",
        "requested_at",
        "rating",
    )
    list_filter = ("status", "requested_at")
    ordering = ("-requested_at",)
    list_per_page = 20
    date_hierarchy = "requested_at"

    # ✅ Actions supplémentaires
    actions = ["mark_completed", "mark_pending"]

    def mark_completed(self, request, queryset):
        queryset.update(status="Completed")
        self.message_user(request, _("Selected rides marked as completed."))
    mark_completed.short_description = "Mark selected rides as completed"

    def mark_pending(self, request, queryset):
        queryset.update(status="Pending")
        self.message_user(request, _("Selected rides marked as pending."))
    mark_pending.short_description = "Mark selected rides as pending"
