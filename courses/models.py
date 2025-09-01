from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models.user_model import User


class Category(models.Model):
    """
    Course category model following Single Responsibility Principle.
    Responsible only for categorizing courses.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Course model following Single Responsibility Principle.
    Responsible only for course information and metadata.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    
    # Course details
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Course metadata
    duration_hours = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_students = models.PositiveIntegerField(default=50)
    current_students = models.PositiveIntegerField(default=0)
    
    # Ratings and reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_published(self):
        """Check if course is published."""
        return self.status == 'published'
    
    @property
    def is_full(self):
        """Check if course is full."""
        return self.current_students >= self.max_students
    
    @property
    def available_slots(self):
        """Get number of available slots."""
        return max(0, self.max_students - self.current_students)


class CourseEnrollment(models.Model):
    """
    Course enrollment model following Single Responsibility Principle.
    Responsible only for managing student enrollments.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'course_enrollments'
        verbose_name = 'Course Enrollment'
        verbose_name_plural = 'Course Enrollments'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"


class CourseRating(models.Model):
    """
    Course rating model following Single Responsibility Principle.
    Responsible only for managing course ratings.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_ratings')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_ratings'
        verbose_name = 'Course Rating'
        verbose_name_plural = 'Course Ratings'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} ({self.rating}/5)" 