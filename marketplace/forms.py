from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Service, Booking, Review, CATEGORY_CHOICES

# Choices for user roles
ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('provider', 'Service Provider'),
]

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with role selection.
    """
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    location = forms.CharField(max_length=255, required=True, help_text="Enter your city or area")
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role', 'location', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update the UserProfile created by signal
            user_profile = user.userprofile
            user_profile.role = self.cleaned_data['role']
            user_profile.location = self.cleaned_data['location']
            user_profile.phone_number = self.cleaned_data.get('phone_number', '')
            user_profile.save()
        return user

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile.
    """
    class Meta:
        model = UserProfile
        fields = ('location', 'phone_number', 'bio', 'profile_photo')

class ServiceForm(forms.ModelForm):
    """
    Form for creating/editing services.
    """
    class Meta:
        model = Service
        fields = ('title', 'description', 'category', 'price', 'location', 'experience_years', 'image')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BookingForm(forms.ModelForm):
    """
    Form for creating bookings.
    """
    class Meta:
        model = Booking
        fields = ('booking_date', 'notes')
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ReviewForm(forms.ModelForm):
    """
    Form for submitting reviews.
    """
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }