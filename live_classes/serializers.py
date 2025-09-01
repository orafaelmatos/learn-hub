from rest_framework import serializers

from .models import (
    LiveClass,
    LiveClassMessage,
    LiveClassParticipant,
    LiveClassRecording,
)


class LiveClassSerializer(serializers.ModelSerializer):
    """
    Live class serializer following Open/Closed Principle.
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveClass
        fields = [
            'id', 'title', 'description', 'course', 'course_title', 'teacher', 'teacher_name',
            'scheduled_at', 'duration_minutes', 'status', 'meeting_url', 'meeting_id',
            'meeting_password', 'max_participants', 'current_participants', 'available_slots',
            'is_public', 'requires_approval', 'will_be_recorded', 'recording_url',
            'total_views', 'participants_count', 'created_at', 'updated_at',
            'started_at', 'ended_at'
        ]
        read_only_fields = [
            'id', 'current_participants', 'total_views', 'created_at', 'updated_at',
            'started_at', 'ended_at'
        ]
    
    def get_participants_count(self, obj):
        return obj.participants.count()


class LiveClassCreateSerializer(serializers.ModelSerializer):
    """
    Live class creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = LiveClass
        fields = [
            'title', 'description', 'course', 'scheduled_at', 'duration_minutes',
            'meeting_url', 'meeting_id', 'meeting_password', 'max_participants',
            'is_public', 'requires_approval', 'will_be_recorded', 'teacher'
        ]
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class LiveClassUpdateSerializer(serializers.ModelSerializer):
    """
    Live class update serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = LiveClass
        fields = [
            'title', 'description', 'scheduled_at', 'duration_minutes',
            'meeting_url', 'meeting_id', 'meeting_password', 'max_participants',
            'is_public', 'requires_approval', 'will_be_recorded', 'status'
        ]


class LiveClassParticipantSerializer(serializers.ModelSerializer):
    """
    Live class participant serializer following Open/Closed Principle.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    live_class_title = serializers.CharField(source='live_class.title', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = LiveClassParticipant
        fields = [
            'id', 'student', 'student_name', 'live_class', 'live_class_title',
            'status', 'joined_at', 'left_at', 'attendance_duration',
            'registered_at', 'approved_at', 'approved_by', 'approved_by_name'
        ]
        read_only_fields = ['id', 'registered_at', 'approved_at']


class LiveClassParticipantCreateSerializer(serializers.ModelSerializer):
    """
    Live class participant creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = LiveClassParticipant
        fields = ['live_class']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class LiveClassMessageSerializer(serializers.ModelSerializer):
    """
    Live class message serializer following Open/Closed Principle.
    """
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    live_class_title = serializers.CharField(source='live_class.title', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveClassMessage
        fields = [
            'id', 'live_class', 'live_class_title', 'sender', 'sender_name',
            'message', 'message_type', 'is_private', 'is_answered',
            'parent_message', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return LiveClassMessageSerializer(replies, many=True).data


class LiveClassMessageCreateSerializer(serializers.ModelSerializer):
    """
    Live class message creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = LiveClassMessage
        fields = ['live_class', 'message', 'message_type', 'is_private', 'parent_message', 'sender']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class LiveClassRecordingSerializer(serializers.ModelSerializer):
    """
    Live class recording serializer following Open/Closed Principle.
    """
    live_class_title = serializers.CharField(source='live_class.title', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = LiveClassRecording
        fields = [
            'id', 'live_class', 'live_class_title', 'title', 'description',
            'recording_url', 'recording_file', 'duration_minutes', 'file_size',
            'file_size_mb', 'is_public', 'is_downloadable', 'view_count',
            'download_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'view_count', 'download_count', 'created_at', 'updated_at'
        ]


class LiveClassRecordingCreateSerializer(serializers.ModelSerializer):
    """
    Live class recording creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = LiveClassRecording
        fields = [
            'live_class', 'title', 'description', 'recording_url', 'recording_file',
            'duration_minutes', 'is_public', 'is_downloadable'
        ]


class LiveClassStatusUpdateSerializer(serializers.Serializer):
    """
    Live class status update serializer following Open/Closed Principle.
    """
    status = serializers.ChoiceField(choices=LiveClass.STATUS_CHOICES)
    
    def validate_status(self, value):
        # Add custom validation logic here if needed
        return value 