from django.urls import path

from .views import (
    LiveClassDetailView,
    LiveClassListView,
    LiveClassMessageListView,
    LiveClassParticipantListView,
    LiveClassRecordingDetailView,
    LiveClassRecordingListView,
    TeacherLiveClassListView,
    approve_participant,
    end_live_class,
    join_live_class,
    leave_live_class,
    start_live_class,
    upcoming_live_classes,
)

app_name = 'live_classes'

urlpatterns = [
    # Live class endpoints
    path('live-classes/', LiveClassListView.as_view(), name='live_class_list'),
    path('live-classes/<int:pk>/', LiveClassDetailView.as_view(), name='live_class_detail'),
    path('live-classes/teacher/', TeacherLiveClassListView.as_view(), name='teacher_live_classes'),
    path('live-classes/upcoming/', upcoming_live_classes, name='upcoming_live_classes'),
    
    # Live class management endpoints
    path('live-classes/<int:live_class_id>/start/', start_live_class, name='start_live_class'),
    path('live-classes/<int:live_class_id>/end/', end_live_class, name='end_live_class'),
    path('live-classes/<int:live_class_id>/join/', join_live_class, name='join_live_class'),
    path('live-classes/<int:live_class_id>/leave/', leave_live_class, name='leave_live_class'),
    
    # Participant endpoints
    path('live-classes/<int:live_class_id>/participants/', LiveClassParticipantListView.as_view(), name='participant_list'),
    path('live-classes/<int:live_class_id>/participants/<int:participant_id>/approve/', approve_participant, name='approve_participant'),
    
    # Message endpoints
    path('live-classes/<int:live_class_id>/messages/', LiveClassMessageListView.as_view(), name='message_list'),
    
    # Recording endpoints
    path('recordings/', LiveClassRecordingListView.as_view(), name='recording_list'),
    path('recordings/<int:pk>/', LiveClassRecordingDetailView.as_view(), name='recording_detail'),
] 