from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import CourseEnrollment
from users.permissions import IsTeacher, IsTeacherOrReadOnly

from .models import (
    LiveClass,
    LiveClassMessage,
    LiveClassParticipant,
    LiveClassRecording,
)
from .serializers import (
    LiveClassCreateSerializer,
    LiveClassMessageCreateSerializer,
    LiveClassMessageSerializer,
    LiveClassParticipantCreateSerializer,
    LiveClassParticipantSerializer,
    LiveClassRecordingCreateSerializer,
    LiveClassRecordingSerializer,
    LiveClassSerializer,
    LiveClassStatusUpdateSerializer,
    LiveClassUpdateSerializer,
)


class LiveClassListView(generics.ListCreateAPIView):
    """
    View for listing and creating live classes.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'teacher', 'status', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_at', 'title', 'created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LiveClassCreateSerializer
        return LiveClassSerializer
    
    def get_queryset(self):
        queryset = LiveClass.objects.all()
        user = self.request.user
        
        # Teachers can see all their live classes
        if user.is_teacher:
            return queryset.filter(teacher=user)
        
        # Students can only see live classes from courses they're enrolled in
        enrolled_courses = CourseEnrollment.objects.filter(
            student=user, is_active=True
        ).values_list('course_id', flat=True)
        return queryset.filter(course_id__in=enrolled_courses)


class LiveClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for live class details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LiveClassUpdateSerializer
        return LiveClassSerializer


class TeacherLiveClassListView(generics.ListAPIView):
    """
    View for listing teacher's live classes.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return LiveClass.objects.filter(teacher=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def start_live_class(request, live_class_id):
    """
    View for starting a live class.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        live_class = LiveClass.objects.get(id=live_class_id, teacher=request.user)
    except LiveClass.DoesNotExist:
        return Response({'error': 'Live class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if live_class.status != 'scheduled':
        return Response({'error': 'Live class is not scheduled'}, status=status.HTTP_400_BAD_REQUEST)
    
    live_class.status = 'live'
    live_class.started_at = timezone.now()
    live_class.save()
    
    serializer = LiveClassSerializer(live_class)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def end_live_class(request, live_class_id):
    """
    View for ending a live class.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        live_class = LiveClass.objects.get(id=live_class_id, teacher=request.user)
    except LiveClass.DoesNotExist:
        return Response({'error': 'Live class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if live_class.status != 'live':
        return Response({'error': 'Live class is not live'}, status=status.HTTP_400_BAD_REQUEST)
    
    live_class.status = 'ended'
    live_class.ended_at = timezone.now()
    live_class.save()
    
    serializer = LiveClassSerializer(live_class)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_live_class(request, live_class_id):
    """
    View for joining a live class.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        live_class = LiveClass.objects.get(id=live_class_id)
    except LiveClass.DoesNotExist:
        return Response({'error': 'Live class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is enrolled in the course
    if not CourseEnrollment.objects.filter(
        student=request.user, 
        course=live_class.course, 
        is_active=True
    ).exists():
        return Response({'error': 'Must be enrolled to join'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if class is full
    if live_class.is_full:
        return Response({'error': 'Live class is full'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update participation
    participation, created = LiveClassParticipant.objects.get_or_create(
        student=request.user,
        live_class=live_class,
        defaults={'status': 'registered'}
    )
    
    if not created and participation.status == 'cancelled':
        participation.status = 'registered'
        participation.save()
    
    # Update participant count
    live_class.current_participants = live_class.participants.filter(status__in=['registered', 'approved', 'attended']).count()
    live_class.save()
    
    serializer = LiveClassParticipantSerializer(participation)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_live_class(request, live_class_id):
    """
    View for leaving a live class.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        participation = LiveClassParticipant.objects.get(
            student=request.user, 
            live_class_id=live_class_id
        )
    except LiveClassParticipant.DoesNotExist:
        return Response({'error': 'Participation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    participation.status = 'cancelled'
    participation.save()
    
    # Update participant count
    live_class = participation.live_class
    live_class.current_participants = live_class.participants.filter(status__in=['registered', 'approved', 'attended']).count()
    live_class.save()
    
    return Response({'message': 'Successfully left live class'})


class LiveClassParticipantListView(generics.ListAPIView):
    """
    View for listing live class participants.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = LiveClassParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        live_class_id = self.kwargs.get('live_class_id')
        return LiveClassParticipant.objects.filter(live_class_id=live_class_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacher])
def approve_participant(request, live_class_id, participant_id):
    """
    View for approving a participant.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        participation = LiveClassParticipant.objects.get(
            id=participant_id,
            live_class_id=live_class_id,
            live_class__teacher=request.user
        )
    except LiveClassParticipant.DoesNotExist:
        return Response({'error': 'Participation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    participation.status = 'approved'
    participation.approved_by = request.user
    participation.approved_at = timezone.now()
    participation.save()
    
    serializer = LiveClassParticipantSerializer(participation)
    return Response(serializer.data)


class LiveClassMessageListView(generics.ListCreateAPIView):
    """
    View for listing and creating live class messages.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = LiveClassMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LiveClassMessageCreateSerializer
        return LiveClassMessageSerializer
    
    def get_queryset(self):
        live_class_id = self.kwargs.get('live_class_id')
        user = self.request.user
        
        # Teachers can see all messages
        live_class = LiveClass.objects.get(id=live_class_id)
        if user.is_teacher and live_class.teacher == user:
            return LiveClassMessage.objects.filter(live_class_id=live_class_id)
        
        # Students can only see public messages and their own private messages
        return LiveClassMessage.objects.filter(
            Q(live_class_id=live_class_id, is_private=False) | Q(live_class_id=live_class_id, sender=user)
        )


class LiveClassRecordingListView(generics.ListCreateAPIView):
    """
    View for listing and creating live class recordings.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = LiveClassRecording.objects.all()
    serializer_class = LiveClassRecordingSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LiveClassRecordingCreateSerializer
        return LiveClassRecordingSerializer
    
    def get_queryset(self):
        queryset = LiveClassRecording.objects.all()
        user = self.request.user
        
        # Teachers can see all their recordings
        if user.is_teacher:
            return queryset.filter(live_class__teacher=user)
        
        # Students can only see recordings from courses they're enrolled in
        enrolled_courses = CourseEnrollment.objects.filter(
            student=user, is_active=True
        ).values_list('course_id', flat=True)
        return queryset.filter(live_class__course_id__in=enrolled_courses)


class LiveClassRecordingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for live class recording details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = LiveClassRecording.objects.all()
    serializer_class = LiveClassRecordingSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_live_classes(request):
    """
    View for getting upcoming live classes.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    user = request.user
    now = timezone.now()
    
    if user.is_teacher:
        # Teachers see their upcoming classes
        live_classes = LiveClass.objects.filter(
            teacher=user,
            scheduled_at__gte=now,
            status='scheduled'
        )
    else:
        # Students see upcoming classes from enrolled courses
        enrolled_courses = CourseEnrollment.objects.filter(
            student=user, is_active=True
        ).values_list('course_id', flat=True)
        live_classes = LiveClass.objects.filter(
            course_id__in=enrolled_courses,
            scheduled_at__gte=now,
            status='scheduled'
        )
    
    serializer = LiveClassSerializer(live_classes, many=True)
    return Response(serializer.data) 