import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserAPITest(APITestCase):
    """Test cases for User API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.profile_url = reverse('users:profile')
        self.teachers_url = reverse('users:teachers_list')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student'
        }
        
        self.teacher_data = {
            'username': 'teacher',
            'email': 'teacher@example.com',
            'password': 'teacherpass123',
            'password_confirm': 'teacherpass123',
            'first_name': 'John',
            'last_name': 'Teacher',
            'user_type': 'teacher'
        }
    
   
    def test_get_user_profile_authenticated(self):
        """Test getting user profile when authenticated."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user.email)
    
    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile when not authenticated."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        self.client.force_authenticate(user=user)
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['bio'], 'Updated bio')
    
    def test_get_teachers_list(self):
        """Test getting list of teachers."""
        # Create a teacher
        teacher = User.objects.create_user(
            username=self.teacher_data['username'],
            email=self.teacher_data['email'],
            password=self.teacher_data['password'],
            first_name=self.teacher_data['first_name'],
            last_name=self.teacher_data['last_name'],
            user_type=self.teacher_data['user_type']
        )
        
        # Create a student
        student = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        
        self.client.force_authenticate(user=student)
        response = self.client.get(self.teachers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], teacher.email)


class UserPermissionsTest(APITestCase):
    """Test cases for user permissions."""
    
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
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123',
            user_type='admin'
        )
    
    def test_teacher_permissions(self):
        """Test teacher-specific permissions."""
        from users.permissions import IsTeacher
        
        permission = IsTeacher()
        
        # Teacher should have permission
        request = type('Request', (), {'user': self.teacher})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Student should not have permission
        request = type('Request', (), {'user': self.student})()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_student_permissions(self):
        """Test student-specific permissions."""
        from users.permissions import IsStudent
        
        permission = IsStudent()
        
        # Student should have permission
        request = type('Request', (), {'user': self.student})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Teacher should not have permission
        request = type('Request', (), {'user': self.teacher})()
        self.assertFalse(permission.has_permission(request, None))
    
    def test_admin_permissions(self):
        """Test admin-specific permissions."""
        from users.permissions import IsAdmin
        
        permission = IsAdmin()
        
        # Admin should have permission
        request = type('Request', (), {'user': self.admin})()
        self.assertTrue(permission.has_permission(request, None))
        
        # Teacher should not have permission
        request = type('Request', (), {'user': self.teacher})()
        self.assertFalse(permission.has_permission(request, None)) 