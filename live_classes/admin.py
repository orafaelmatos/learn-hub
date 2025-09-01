from django.contrib import admin

from .models import (
    LiveClass,
    LiveClassMessage,
    LiveClassParticipant,
    LiveClassRecording,
)


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    """
    Admin configuration for LiveClass model.
    """
    list_display = ('title', 'course', 'teacher', 'scheduled_at', 'duration_minutes', 'status', 'current_participants', 'max_participants', 'created_at')
    list_filter = ('status', 'is_public', 'requires_approval', 'will_be_recorded', 'scheduled_at', 'created_at')
    search_fields = ('title', 'description', 'course__title', 'teacher__email', 'teacher__first_name', 'teacher__last_name')
    ordering = ('-scheduled_at',)
    readonly_fields = ('current_participants', 'total_views', 'created_at', 'updated_at', 'started_at', 'ended_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'teacher')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'duration_minutes', 'status')
        }),
        ('Meeting Details', {
            'fields': ('meeting_url', 'meeting_id', 'meeting_password')
        }),
        ('Access Control', {
            'fields': ('max_participants', 'current_participants', 'is_public', 'requires_approval')
        }),
        ('Recording', {
            'fields': ('will_be_recorded', 'recording_url')
        }),
        ('Statistics', {
            'fields': ('total_views',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LiveClassParticipant)
class LiveClassParticipantAdmin(admin.ModelAdmin):
    """
    Admin configuration for LiveClassParticipant model.
    """
    list_display = ('student', 'live_class', 'status', 'joined_at', 'left_at', 'attendance_duration', 'registered_at')
    list_filter = ('status', 'registered_at', 'approved_at', 'joined_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'live_class__title')
    ordering = ('-registered_at',)
    readonly_fields = ('registered_at', 'approved_at')


@admin.register(LiveClassMessage)
class LiveClassMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for LiveClassMessage model.
    """
    list_display = ('sender', 'live_class', 'message_type', 'is_private', 'is_answered', 'created_at')
    list_filter = ('message_type', 'is_private', 'is_answered', 'created_at')
    search_fields = ('message', 'sender__email', 'sender__first_name', 'sender__last_name', 'live_class__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LiveClassRecording)
class LiveClassRecordingAdmin(admin.ModelAdmin):
    """
    Admin configuration for LiveClassRecording model.
    """
    list_display = ('title', 'live_class', 'duration_minutes', 'file_size_mb', 'is_public', 'is_downloadable', 'view_count', 'download_count', 'created_at')
    list_filter = ('is_public', 'is_downloadable', 'created_at')
    search_fields = ('title', 'description', 'live_class__title')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'view_count', 'download_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'live_class')
        }),
        ('Recording Details', {
            'fields': ('recording_url', 'recording_file', 'duration_minutes', 'file_size')
        }),
        ('Access Control', {
            'fields': ('is_public', 'is_downloadable')
        }),
        ('Statistics', {
            'fields': ('view_count', 'download_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 