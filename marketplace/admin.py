from django.contrib import admin
from .models import UserProfile, Service, Booking, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'location', 'phone_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'location')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'price', 'location', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'provider__username', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'status', 'booking_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'service__title')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer__username', 'service__title')
