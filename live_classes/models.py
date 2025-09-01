from django.core.validators import MinValueValidator
from django.db import models

from courses.models import Course
from users.models.user_model import User


class LiveClass(models.Model):
    """
    Live class model following Single Responsibility Principle.
    Responsible only for live class information and scheduling.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_classes_taught')
    
    # Scheduling
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(15)],
        help_text='Duration in minutes (minimum 15)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Meeting details
    meeting_url = models.URLField(blank=True, help_text='Zoom, Google Meet, or other meeting URL')
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Access control
    max_participants = models.PositiveIntegerField(default=50)
    is_public = models.BooleanField(default=False, help_text='Available to all enrolled students')
    requires_approval = models.BooleanField(default=False, help_text='Teacher approval required to join')
    
    # Recording
    will_be_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)
    
    # Metadata
    current_participants = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'live_classes'
        verbose_name = 'Live Class'
        verbose_name_plural = 'Live Classes'
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    @property
    def is_live(self):
        """Check if class is currently live."""
        return self.status == 'live'
    
    @property
    def is_scheduled(self):
        """Check if class is scheduled."""
        return self.status == 'scheduled'
    
    @property
    def is_ended(self):
        """Check if class has ended."""
        return self.status == 'ended'
    
    @property
    def is_full(self):
        """Check if class is full."""
        return self.current_participants >= self.max_participants
    
    @property
    def available_slots(self):
        """Get number of available slots."""
        return max(0, self.max_participants - self.current_participants)


class LiveClassParticipant(models.Model):
    """
    Live class participant model following Single Responsibility Principle.
    Responsible only for managing participant registrations and attendance.
    """
    PARTICIPANT_STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('approved', 'Approved'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_class_participations')
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='participants')
    status = models.CharField(max_length=20, choices=PARTICIPANT_STATUS_CHOICES, default='registered')
    
    # Attendance tracking
    joined_at = models.DateTimeField(blank=True, null=True)
    left_at = models.DateTimeField(blank=True, null=True)
    attendance_duration = models.PositiveIntegerField(default=0, help_text='Attendance duration in minutes')
    
    # Registration
    registered_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='approved_participations'
    )
    
    class Meta:
        db_table = 'live_class_participants'
        verbose_name = 'Live Class Participant'
        verbose_name_plural = 'Live Class Participants'
        unique_together = ['student', 'live_class']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.live_class.title}"


class LiveClassMessage(models.Model):
    """
    Live class message model following Single Responsibility Principle.
    Responsible only for managing chat messages during live classes.
    """
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_class_messages')
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('system', 'System'),
    ], default='text')
    
    # Message metadata
    is_private = models.BooleanField(default=False, help_text='Private message to teacher')
    is_answered = models.BooleanField(default=False, help_text='Question has been answered')
    parent_message = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, 
        related_name='replies'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'live_class_messages'
        verbose_name = 'Live Class Message'
        verbose_name_plural = 'Live Class Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.message[:50]}..."


class LiveClassRecording(models.Model):
    """
    Live class recording model following Single Responsibility Principle.
    Responsible only for managing recorded sessions.
    """
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='recordings')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Recording details
    recording_url = models.URLField()
    recording_file = models.FileField(upload_to='live_class_recordings/', blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0, help_text='File size in bytes')
    
    # Access control
    is_public = models.BooleanField(default=False, help_text='Available to all enrolled students')
    is_downloadable = models.BooleanField(default=False, help_text='Students can download recording')
    
    # Metadata
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'live_class_recordings'
        verbose_name = 'Live Class Recording'
        verbose_name_plural = 'Live Class Recordings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.live_class.title}"
    
    @property
    def file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2) 