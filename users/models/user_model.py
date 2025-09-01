from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """
    Custom User model following Single Responsibility Principle.
    Responsible only for user authentication and basic profile information.
    """
    
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('admin', 'Administrator'),
    ]
    
    # Basic profile fields
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Required fields for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_teacher(self):
        """Check if user is a teacher."""
        return self.user_type == 'teacher'
    
    @property
    def is_student(self):
        """Check if user is a student."""
        return self.user_type == 'student'
    
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.user_type == 'admin'
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() 