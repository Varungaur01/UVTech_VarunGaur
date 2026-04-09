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

# Choices for payment status
PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

# Choices for transaction type
TRANSACTION_TYPE_CHOICES = [
    ('service_payment', 'Service Payment'),
    ('commission_payment', 'Commission Payment'),
    ('refund', 'Refund'),
]

# Commission percentage
COMPANY_COMMISSION_PERCENTAGE = 20

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
    is_paid = models.BooleanField(default=False, help_text="Whether payment is completed")
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


class Payment(models.Model):
    """
    Represents a payment transaction for a service booking.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    company_commission = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    provider_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    razorpay_order_id = models.CharField(max_length=255, blank=True, help_text="Razorpay Order ID")
    razorpay_payment_id = models.CharField(max_length=255, blank=True, help_text="Razorpay Payment ID")
    razorpay_signature = models.CharField(max_length=255, blank=True, help_text="Razorpay Payment Signature")
    payment_method = models.CharField(max_length=50, default='card', help_text="Payment method used (card, netbanking, upi, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment of {self.amount} for {self.booking.id} - {self.status}"

    def save(self, *args, **kwargs):
        # Auto calculate commission and provider amount if not set
        if not self.company_commission:
            self.company_commission = (self.amount * COMPANY_COMMISSION_PERCENTAGE) / 100
        if not self.provider_amount:
            self.provider_amount = self.amount - self.company_commission
        super().save(*args, **kwargs)


class ProviderBalance(models.Model):
    """
    Tracks the balance and commission owed by each service provider.
    Negative balance means provider owes commission to the company.
    """
    provider = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_balance')
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_commission_owed = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Positive: money owed to provider, Negative: provider owes commission")
    is_suspended = models.BooleanField(default=False, help_text="Suspend if balance is negative for too long")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Provider Balance"
        verbose_name_plural = "Provider Balances"

    def __str__(self):
        return f"{self.provider.username} - Balance: {self.current_balance}"

    def update_balance(self):
        """Update the provider's current balance"""
        self.current_balance = self.total_earnings - self.total_commission_owed
        # Suspend if balance is negative (provider owes commission)
        self.is_suspended = self.current_balance < 0
        self.save()


class PaymentOrder(models.Model):
    """
    Stores payment orders with QR codes for easy payment processing.
    """
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment_order')
    order_id = models.CharField(max_length=255, unique=True, help_text="Razorpay Order ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True, help_text="QR code for payment")
    short_url = models.CharField(max_length=255, blank=True, help_text="Razorpay short URL")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField(help_text="Order expiration time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"


class CommissionTransaction(models.Model):
    """
    Tracks all commission-related transactions for audit trail.
    """
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commission_transactions')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='commission_transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.provider.username} - {self.amount}"
