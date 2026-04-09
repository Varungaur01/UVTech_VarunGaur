from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserProfile, Service, Booking, Review, Conversation, Message, CATEGORY_CHOICES
from .forms import UserRegistrationForm, UserProfileForm, ServiceForm, BookingForm, ReviewForm

def home(request):
    """
    Home page view.
    """
    # Get featured services (active services with high ratings or recent)
    featured_services = Service.objects.filter(is_active=True).order_by('-created_at')[:6]
    categories = CATEGORY_CHOICES
    context = {
        'featured_services': featured_services,
        'categories': categories,
    }
    return render(request, 'marketplace/home.html', context)

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
        reviews = Review.objects.filter(service__provider=request.user)
        
        # Calculate stats
        total_services = services.count()
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='completed').count()
        pending_bookings = bookings.filter(status='pending').count()
        
        if reviews:
            average_rating = sum(review.rating for review in reviews) / len(reviews)
            is_top_rated = average_rating >= 4.0
        else:
            average_rating = 0
            is_top_rated = False
        
        context = {
            'user_profile': user_profile,
            'services': services,
            'bookings': bookings.order_by('-created_at'),
            'total_services': total_services,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'pending_bookings': pending_bookings,
            'average_rating': average_rating,
            'is_top_rated': is_top_rated,
            'review_count': reviews.count(),
        }
        return render(request, 'marketplace/provider_dashboard.html', context)
    else:
        # Customer dashboard
        bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
        reviews = Review.objects.filter(customer=request.user)
        
        # Calculate stats
        total_bookings = bookings.count()
        completed_bookings = bookings.filter(status='completed').count()
        pending_bookings = bookings.filter(status='pending').count()
        reviews_given = reviews.count()
        
        context = {
            'user_profile': user_profile,
            'bookings': bookings,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'pending_bookings': pending_bookings,
            'reviews_given': reviews_given,
        }
        return render(request, 'marketplace/customer_dashboard.html', context)

@login_required
def profile(request):
    """
    User profile view and edit.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
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
    from django.db.models import Avg
    
    services = Service.objects.filter(is_active=True).prefetch_related('reviews')
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

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price_low':
        services = services.order_by('price')
    elif sort == 'price_high':
        services = services.order_by('-price')
    elif sort == 'rating':
        # Sort by average rating (calculated in Python for now)
        services_list = list(services)
        services_list.sort(key=lambda s: s.average_rating(), reverse=True)
        # Convert back to queryset for pagination
        services = services.model.objects.filter(pk__in=[s.pk for s in services_list])
    else:
        services = services.order_by(sort)

    context = {
        'services': services,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_sort': sort,
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
        form = ServiceForm(request.POST, request.FILES)
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
        form = ServiceForm(request.POST, request.FILES, instance=service)
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
            Conversation.objects.get_or_create(
                customer=request.user,
                provider=service.provider,
                booking=booking
            )
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
            Conversation.objects.get_or_create(
                customer=booking.customer,
                provider=booking.service.provider,
                booking=booking
            )
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

@login_required
def delete_service(request, pk):
    """
    Delete a service (providers only).
    """
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'marketplace/delete_service.html', {'service': service})

def provider_profile(request, user_id):
    """
    View provider profile and their services/reviews.
    """
    provider = get_object_or_404(User, pk=user_id)
    try:
        user_profile = provider.userprofile
        if user_profile.role != 'provider':
            messages.error(request, 'This user is not a service provider.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')

    services = Service.objects.filter(provider=provider, is_active=True)
    reviews = Review.objects.filter(service__provider=provider).select_related('customer', 'service', 'booking')
    
    # Calculate stats
    total_services = services.count()
    total_bookings = Booking.objects.filter(service__provider=provider).count()
    completed_bookings = Booking.objects.filter(service__provider=provider, status='completed').count()
    
    if reviews:
        average_rating = sum(review.rating for review in reviews) / len(reviews)
        is_top_rated = average_rating >= 4.0
    else:
        average_rating = 0
        is_top_rated = False

    context = {
        'provider': provider,
        'user_profile': user_profile,
        'services': services,
        'reviews': reviews.order_by('-created_at'),
        'total_services': total_services,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'average_rating': average_rating,
        'is_top_rated': is_top_rated,
        'review_count': reviews.count(),
    }
    return render(request, 'marketplace/provider_profile.html', context)

# ============ MESSAGING VIEWS ============

@login_required
def messages_inbox(request):
    """
    Display all conversations for the logged-in user.
    """
    # Get conversations where user is sender or receiver
    conversations = Conversation.objects.filter(
        Q(customer=request.user) | Q(provider=request.user)
    ).prefetch_related('messages', 'customer', 'provider').annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-updated_at')
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'marketplace/messages_inbox.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """
    Display a specific conversation with message history.
    """
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id
    )
    
    # Check if user is part of this conversation
    if request.user != conversation.customer and request.user != conversation.provider:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('messages_inbox')
    
    # Mark messages as read
    Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages
    messages_list = conversation.messages.all().order_by('created_at')
    
    # Determine the other user in conversation
    if request.user == conversation.customer:
        other_user = conversation.provider
    else:
        other_user = conversation.customer
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
            )
            conversation.save()  # Update the updated_at timestamp
            return redirect('conversation_detail', conversation_id=conversation.id)
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'other_user': other_user,
    }
    return render(request, 'marketplace/conversation_detail.html', context)

@login_required
def start_conversation(request, user_id):
    """
    Start or redirect to existing conversation with a specific user.
    """
    other_user = get_object_or_404(User, pk=user_id)
    
    if request.user == other_user:
        messages.error(request, 'You cannot message yourself.')
        return redirect('dashboard')
    
    # Check if conversation already exists
    conversation = Conversation.objects.filter(
        (Q(customer=request.user) & Q(provider=other_user)) |
        (Q(customer=other_user) & Q(provider=request.user))
    ).first()
    
    if not conversation:
        # Determine who is customer and who is provider based on roles
        user_profile = get_object_or_404(UserProfile, user=request.user)
        other_profile = get_object_or_404(UserProfile, user=other_user)
        
        if user_profile.role == 'customer' and other_profile.role == 'provider':
            conversation = Conversation.objects.create(
                customer=request.user,
                provider=other_user
            )
        elif user_profile.role == 'provider' and other_profile.role == 'customer':
            conversation = Conversation.objects.create(
                customer=other_user,
                provider=request.user
            )
        else:
            messages.error(request, 'Invalid user types for messaging.')
            return redirect('dashboard')
    
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
def start_conversation_from_booking(request, booking_id):
    """
    Start a conversation from a booking.
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if user is customer or provider of this booking
    if request.user != booking.customer and request.user != booking.service.provider:
        messages.error(request, 'You do not have access to this booking.')
        return redirect('dashboard')
    
    # Determine the other user
    if request.user == booking.customer:
        other_user = booking.service.provider
    else:
        other_user = booking.customer
    
    # Check or create conversation
    conversation = Conversation.objects.filter(
        (Q(customer=request.user) & Q(provider=other_user)) |
        (Q(customer=other_user) & Q(provider=request.user)),
        booking=booking
    ).first()
    
    if not conversation:
        if request.user == booking.customer:
            conversation = Conversation.objects.create(
                customer=booking.customer,
                provider=booking.service.provider,
                booking=booking
            )
        else:
            conversation = Conversation.objects.create(
                customer=booking.customer,
                provider=booking.service.provider,
                booking=booking
            )
    
    return redirect('conversation_detail', conversation_id=conversation.id)
