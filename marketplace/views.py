from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import UserProfile, Service, Booking, Review, CATEGORY_CHOICES
from .forms import UserRegistrationForm, UserProfileForm, ServiceForm, BookingForm, ReviewForm

def home(request):
    """
    Home page view.
    """
    return render(request, 'marketplace/home.html')

def register(request):
    """
    User registration view with role selection.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def user_login(request):
    """
    User login view.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'marketplace/login.html')

def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    """
    Dashboard view - different for customers and providers.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.role == 'provider':
        # Provider dashboard
        services = Service.objects.filter(provider=request.user)
        bookings = Booking.objects.filter(service__provider=request.user)
        context = {
            'user_profile': user_profile,
            'services': services,
            'bookings': bookings,
        }
        return render(request, 'marketplace/provider_dashboard.html', context)
    else:
        # Customer dashboard
        bookings = Booking.objects.filter(customer=request.user)
        context = {
            'user_profile': user_profile,
            'bookings': bookings,
        }
        return render(request, 'marketplace/customer_dashboard.html', context)

@login_required
def profile(request):
    """
    User profile view and edit.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'marketplace/profile.html', {'form': form, 'user_profile': user_profile})

@login_required
def service_list(request):
    """
    List all active services with search and filter options.
    """
    services = Service.objects.filter(is_active=True)
    categories = CATEGORY_CHOICES

    # Search functionality
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(provider__username__icontains=query)
        )

    # Category filter
    category = request.GET.get('category')
    if category:
        services = services.filter(category=category)

    # Location filter
    location = request.GET.get('location')
    if location:
        services = services.filter(location__icontains=location)

    context = {
        'services': services,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'location': location,
    }
    return render(request, 'marketplace/service_list.html', context)

@login_required
def service_detail(request, pk):
    """
    Service detail view.
    """
    service = get_object_or_404(Service, pk=pk, is_active=True)
    reviews = Review.objects.filter(service=service)

    # Check if user can book this service
    can_book = request.user != service.provider and not Booking.objects.filter(
        customer=request.user, service=service, status__in=['pending', 'accepted']
    ).exists()

    context = {
        'service': service,
        'reviews': reviews,
        'can_book': can_book,
        'average_rating': service.average_rating(),
    }
    return render(request, 'marketplace/service_detail.html', context)

@login_required
def create_service(request):
    """
    Create a new service (providers only).
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role != 'provider':
        messages.error(request, 'Only service providers can create services.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service created successfully!')
            return redirect('dashboard')
    else:
        form = ServiceForm()
    return render(request, 'marketplace/create_service.html', {'form': form})

@login_required
def edit_service(request, pk):
    """
    Edit an existing service (providers only).
    """
    service = get_object_or_404(Service, pk=pk, provider=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('dashboard')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'marketplace/edit_service.html', {'form': form, 'service': service})

@login_required
def book_service(request, pk):
    """
    Book a service (customers only).
    """
    service = get_object_or_404(Service, pk=pk, is_active=True)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.role != 'customer':
        messages.error(request, 'Only customers can book services.')
        return redirect('service_detail', pk=pk)

    # Check if already booked
    existing_booking = Booking.objects.filter(
        customer=request.user, service=service, status__in=['pending', 'accepted']
    ).exists()
    if existing_booking:
        messages.error(request, 'You already have a pending or accepted booking for this service.')
        return redirect('service_detail', pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.service = service
            booking.save()
            messages.success(request, 'Booking request sent successfully!')
            return redirect('dashboard')
    else:
        form = BookingForm()
    return render(request, 'marketplace/book_service.html', {'form': form, 'service': service})

@login_required
def manage_bookings(request):
    """
    Manage bookings (providers only).
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role != 'provider':
        messages.error(request, 'Only service providers can manage bookings.')
        return redirect('dashboard')

    bookings = Booking.objects.filter(service__provider=request.user).order_by('-created_at')

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = get_object_or_404(Booking, pk=booking_id, service__provider=request.user)

        if action == 'accept':
            booking.status = 'accepted'
            booking.save()
            messages.success(request, 'Booking accepted!')
        elif action == 'reject':
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking rejected!')
        elif action == 'complete':
            booking.status = 'completed'
            booking.save()
            messages.success(request, 'Booking marked as completed!')

    return render(request, 'marketplace/manage_bookings.html', {'bookings': bookings})

@login_required
def submit_review(request, booking_id):
    """
    Submit a review for a completed booking (customers only).
    """
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user, status='completed')

    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.error(request, 'You have already submitted a review for this booking.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.customer = request.user
            review.service = booking.service
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('dashboard')
    else:
        form = ReviewForm()
    return render(request, 'marketplace/submit_review.html', {'form': form, 'booking': booking})
