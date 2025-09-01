from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from courses.models import Category, Course, CourseEnrollment

from .models import (
    LiveClass,
    LiveClassMessage,
    LiveClassParticipant,
    LiveClassRecording,
)

User = get_user_model()


class LiveClassModelTest(TestCase):
    """Test cases for LiveClass model."""
    
    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50
        )
        
        self.live_class_data = {
            'title': 'Live Python Session',
            'description': 'Live coding session',
            'course': self.course,
            'teacher': self.teacher,
            'scheduled_at': timezone.now() + timedelta(hours=1),
            'duration_minutes': 60,
            'meeting_url': 'https://zoom.us/j/123456789',
            'meeting_id': '123456789',
            'max_participants': 30,
            'is_public': True,
            'will_be_recorded': True
        }
    
    def test_create_live_class(self):
        """Test creating a new live class."""
        live_class = LiveClass.objects.create(**self.live_class_data)
        self.assertEqual(live_class.title, self.live_class_data['title'])
        self.assertEqual(live_class.teacher, self.teacher)
        self.assertEqual(live_class.course, self.course)
        self.assertEqual(live_class.status, 'scheduled')
    
    def test_live_class_str_representation(self):
        """Test live class string representation."""
        live_class = LiveClass.objects.create(**self.live_class_data)
        expected = f"{live_class.title} - {self.course.title}"
        self.assertEqual(str(live_class), expected)
    
    def test_live_class_properties(self):
        """Test live class properties."""
        live_class = LiveClass.objects.create(**self.live_class_data)
        
        self.assertTrue(live_class.is_scheduled)
        self.assertFalse(live_class.is_live)
        self.assertFalse(live_class.is_ended)
        self.assertFalse(live_class.is_full)
        self.assertEqual(live_class.available_slots, 30)
        
        # Test when class is full
        live_class.current_participants = 30
        live_class.save()
        self.assertTrue(live_class.is_full)
        self.assertEqual(live_class.available_slots, 0)
        
        # Test when class is live
        live_class.status = 'live'
        live_class.save()
        self.assertTrue(live_class.is_live)
        self.assertFalse(live_class.is_scheduled)
        
        # Test when class is ended
        live_class.status = 'ended'
        live_class.save()
        self.assertTrue(live_class.is_ended)


class LiveClassParticipantModelTest(TestCase):
    """Test cases for LiveClassParticipant model."""
    
    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50
        )
        
        self.live_class = LiveClass.objects.create(
            title='Live Python Session',
            description='Live coding session',
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            max_participants=30
        )
    
    def test_create_participant(self):
        """Test creating a new participant."""
        participant = LiveClassParticipant.objects.create(
            student=self.student,
            live_class=self.live_class
        )
        self.assertEqual(participant.student, self.student)
        self.assertEqual(participant.live_class, self.live_class)
        self.assertEqual(participant.status, 'registered')
    
    def test_participant_str_representation(self):
        """Test participant string representation."""
        participant = LiveClassParticipant.objects.create(
            student=self.student,
            live_class=self.live_class
        )
        expected = f"{self.student.get_full_name()} - {self.live_class.title}"
        self.assertEqual(str(participant), expected)


class LiveClassMessageModelTest(TestCase):
    """Test cases for LiveClassMessage model."""
    
    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50
        )
        
        self.live_class = LiveClass.objects.create(
            title='Live Python Session',
            description='Live coding session',
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            max_participants=30
        )
    
    def test_create_message(self):
        """Test creating a new message."""
        message = LiveClassMessage.objects.create(
            live_class=self.live_class,
            sender=self.student,
            message='Hello everyone!',
            message_type='text'
        )
        self.assertEqual(message.live_class, self.live_class)
        self.assertEqual(message.sender, self.student)
        self.assertEqual(message.message, 'Hello everyone!')
        self.assertEqual(message.message_type, 'text')
    
    def test_message_str_representation(self):
        """Test message string representation."""
        message = LiveClassMessage.objects.create(
            live_class=self.live_class,
            sender=self.student,
            message='Hello everyone!',
            message_type='text'
        )
        expected = f"{self.student.get_full_name()}: Hello everyone!..."
        self.assertEqual(str(message), expected)
    
    def test_message_replies(self):
        """Test message replies."""
        parent_message = LiveClassMessage.objects.create(
            live_class=self.live_class,
            sender=self.student,
            message='Question about Python?',
            message_type='question'
        )
        
        reply = LiveClassMessage.objects.create(
            live_class=self.live_class,
            sender=self.teacher,
            message='Great question! Here is the answer...',
            message_type='answer',
            parent_message=parent_message
        )
        
        self.assertEqual(reply.parent_message, parent_message)
        self.assertEqual(parent_message.replies.count(), 1)


class LiveClassRecordingModelTest(TestCase):
    """Test cases for LiveClassRecording model."""
    
    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50
        )
        
        self.live_class = LiveClass.objects.create(
            title='Live Python Session',
            description='Live coding session',
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            max_participants=30
        )
        
        self.recording_data = {
            'live_class': self.live_class,
            'title': 'Recording - Live Python Session',
            'description': 'Recording of the live Python session',
            'recording_url': 'https://example.com/recording.mp4',
            'duration_minutes': 60,
            'file_size': 1024000,  # 1MB
            'is_public': True,
            'is_downloadable': False
        }
    
    def test_create_recording(self):
        """Test creating a new recording."""
        recording = LiveClassRecording.objects.create(**self.recording_data)
        self.assertEqual(recording.live_class, self.live_class)
        self.assertEqual(recording.title, self.recording_data['title'])
        self.assertEqual(recording.duration_minutes, 60)
    
    def test_recording_str_representation(self):
        """Test recording string representation."""
        recording = LiveClassRecording.objects.create(**self.recording_data)
        expected = f"{recording.title} - {self.live_class.title}"
        self.assertEqual(str(recording), expected)
    
    def test_recording_properties(self):
        """Test recording properties."""
        recording = LiveClassRecording.objects.create(**self.recording_data)
        self.assertEqual(recording.file_size_mb, 0.98)  # 1MB = 1024KB, so 1024000 bytes = 0.98 MB


class LiveClassAPITest(APITestCase):
    """Test cases for LiveClass API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.live_class_list_url = reverse('live_classes:live_class_list')
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50,
            status='published'
        )
        
        # Enroll student in course
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        self.live_class_data = {
            'title': 'Live Python Session',
            'description': 'Live coding session',
            'course': self.course.id,
            'scheduled_at': (timezone.now() + timedelta(hours=1)).isoformat(),
            'duration_minutes': 60,
            'meeting_url': 'https://zoom.us/j/123456789',
            'meeting_id': '123456789',
            'max_participants': 30,
            'is_public': True,
            'will_be_recorded': True,
            'teacher': self.teacher.id
        }
    
    def test_create_live_class_as_teacher(self):
        """Test creating a live class as a teacher."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.live_class_list_url, self.live_class_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.live_class_data['title'])
        self.assertEqual(response.data['teacher'], self.teacher.id)
    
    def test_create_live_class_as_student_forbidden(self):
        """Test that students cannot create live classes."""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.live_class_list_url, self.live_class_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_live_classes(self):
        """Test listing live classes."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public']
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.live_class_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_live_class_detail(self):
        """Test getting live class details."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public']
        )
        
        url = reverse('live_classes:live_class_detail', kwargs={'pk': live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], live_class.title)
    
    def test_start_live_class(self):
        """Test starting a live class."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public']
        )
        
        url = reverse('live_classes:start_live_class', kwargs={'live_class_id': live_class.pk})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        live_class.refresh_from_db()
        self.assertEqual(live_class.status, 'live')
        self.assertIsNotNone(live_class.started_at)
    
    def test_end_live_class(self):
        """Test ending a live class."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public'],
            status='live',
            started_at=timezone.now()
        )
        
        url = reverse('live_classes:end_live_class', kwargs={'live_class_id': live_class.pk})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        live_class.refresh_from_db()
        self.assertEqual(live_class.status, 'ended')
        self.assertIsNotNone(live_class.ended_at)
    
    def test_join_live_class(self):
        """Test joining a live class."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public']
        )
        
        url = reverse('live_classes:join_live_class', kwargs={'live_class_id': live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if participant was created
        self.assertTrue(LiveClassParticipant.objects.filter(
            student=self.student,
            live_class=live_class
        ).exists())
        
        # Check if participant count was updated
        live_class.refresh_from_db()
        self.assertEqual(live_class.current_participants, 1)
    
    def test_join_full_live_class(self):
        """Test joining a full live class."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=1,
            current_participants=1,
            is_public=self.live_class_data['is_public']
        )
        
        url = reverse('live_classes:join_live_class', kwargs={'live_class_id': live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_leave_live_class(self):
        """Test leaving a live class."""
        live_class = LiveClass.objects.create(
            title=self.live_class_data['title'],
            description=self.live_class_data['description'],
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=self.live_class_data['duration_minutes'],
            max_participants=self.live_class_data['max_participants'],
            is_public=self.live_class_data['is_public']
        )
        
        participant = LiveClassParticipant.objects.create(
            student=self.student,
            live_class=live_class
        )
        
        # Update participant count
        live_class.current_participants = 1
        live_class.save()
        
        url = reverse('live_classes:leave_live_class', kwargs={'live_class_id': live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if participant was deactivated
        participant.refresh_from_db()
        self.assertEqual(participant.status, 'cancelled')
        
        # Check if participant count was updated
        live_class.refresh_from_db()
        self.assertEqual(live_class.current_participants, 0)


class LiveClassMessageAPITest(APITestCase):
    """Test cases for LiveClassMessage API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50,
            status='published'
        )
        
        # Enroll student in course
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        self.live_class = LiveClass.objects.create(
            title='Live Python Session',
            description='Live coding session',
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            max_participants=30,
            is_public=True
        )
        
        self.message_data = {
            'live_class': self.live_class.id,
            'message': 'Hello everyone!',
            'message_type': 'text',
            'sender': self.student.id,
        }
    
    def test_create_message(self):
        """Test creating a new message."""
        url = reverse('live_classes:message_list', kwargs={'live_class_id': self.live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, self.message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], self.message_data['message'])
        self.assertEqual(response.data['sender'], self.student.id)
    
    def test_list_messages(self):
        """Test listing messages."""
        message = LiveClassMessage.objects.create(
            live_class=self.live_class,
            sender=self.student,
            message=self.message_data['message'],
            message_type=self.message_data['message_type'],
            parent_message=None
        )
        
        url = reverse('live_classes:message_list', kwargs={'live_class_id': self.live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['message'], message.message)
    
    def test_create_private_message(self):
        """Test creating a private message."""
        self.message_data['is_private'] = True
        url = reverse('live_classes:message_list', kwargs={'live_class_id': self.live_class.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, self.message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_private'])


class LiveClassRecordingAPITest(APITestCase):
    """Test cases for LiveClassRecording API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.recording_list_url = reverse('live_classes:recording_list')
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        
        self.course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=50,
            status='published'
        )
        
        # Enroll student in course
        CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        self.live_class = LiveClass.objects.create(
            title='Live Python Session',
            description='Live coding session',
            course=self.course,
            teacher=self.teacher,
            scheduled_at=timezone.now() + timedelta(hours=1),
            duration_minutes=60,
            max_participants=30,
            is_public=True
        )
        
        self.recording_data = {
            'live_class': self.live_class.id,
            'title': 'Recording - Live Python Session',
            'description': 'Recording of the live Python session',
            'recording_url': 'https://example.com/recording.mp4',
            'duration_minutes': 60,
            'is_public': True,
            'is_downloadable': False
        }
    
    def test_create_recording_as_teacher(self):
        """Test creating a recording as a teacher."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.recording_list_url, self.recording_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.recording_data['title'])
        self.assertEqual(response.data['live_class'], self.live_class.id)
    
    def test_create_recording_as_student_forbidden(self):
        """Test that students cannot create recordings."""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.recording_list_url, self.recording_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_recordings(self):
        """Test listing recordings."""
        recording = LiveClassRecording.objects.create(
            live_class=self.live_class,
            title=self.recording_data['title'],
            description=self.recording_data['description'],
            recording_url=self.recording_data['recording_url'],
            duration_minutes=self.recording_data['duration_minutes'],
            is_public=self.recording_data['is_public'],
            is_downloadable=self.recording_data['is_downloadable']
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.recording_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], recording.title)
    
    def test_get_recording_detail(self):
        """Test getting recording details."""
        recording = LiveClassRecording.objects.create(
            live_class=self.live_class,
            title=self.recording_data['title'],
            description=self.recording_data['description'],
            recording_url=self.recording_data['recording_url'],
            duration_minutes=self.recording_data['duration_minutes'],
            is_public=self.recording_data['is_public'],
            is_downloadable=self.recording_data['is_downloadable']
        )
        
        url = reverse('live_classes:recording_detail', kwargs={'pk': recording.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], recording.title) 