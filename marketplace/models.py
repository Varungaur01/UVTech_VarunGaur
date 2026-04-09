from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Choices for user roles
ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('provider', 'Service Provider'),
]

# Choices for service categories
CATEGORY_CHOICES = [
    ('plumber', 'Plumber'),
    ('electrician', 'Electrician'),
    ('tutor', 'Tutor'),
    ('delivery', 'Delivery Agent'),
    ('cleaner', 'Cleaner'),
    ('mechanic', 'Mechanic'),
    ('other', 'Other'),
]

# Choices for booking status
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

class UserProfile(models.Model):
    """
    Extends Django's User model to add role and location information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    location = models.CharField(max_length=255, blank=True, help_text="City or area where the user is located")
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, help_text="Short description for service providers")
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, help_text="Upload your profile photo")

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Service(models.Model):
    """
    Represents a service offered by a service provider.
    """
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255, help_text="Service area or city")
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of experience")
    image = models.ImageField(upload_to='services/', null=True, blank=True, help_text="Upload a service image")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.provider.username}"

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

class Booking(models.Model):
    """
    Represents a booking request from a customer to a service provider.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_made')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField()
    notes = models.TextField(blank=True, help_text="Additional notes from customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking by {self.customer.username} for {self.service.title}"

class Review(models.Model):
    """
    Represents a review and rating given by a customer to a service provider after booking completion.
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.username} - {self.rating} stars"

class Conversation(models.Model):
    """
    Represents a conversation between a customer and a service provider.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_customer')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_provider')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'provider', 'booking')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation between {self.customer.username} and {self.provider.username}"

    def last_message(self):
        return self.messages.first()

class Message(models.Model):
    """
    Represents an individual message in a conversation between customer and provider.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
