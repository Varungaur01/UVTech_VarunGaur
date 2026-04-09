from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('provider/<int:user_id>/', views.provider_profile, name='provider_profile'),
    path('services/', views.service_list, name='service_list'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/<int:pk>/edit/', views.edit_service, name='edit_service'),
    path('services/<int:pk>/delete/', views.delete_service, name='delete_service'),
    path('services/<int:pk>/book/', views.book_service, name='book_service'),
    path('bookings/manage/', views.manage_bookings, name='manage_bookings'),
    path('reviews/<int:booking_id>/submit/', views.submit_review, name='submit_review'),
]