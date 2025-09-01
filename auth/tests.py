import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student'
        }
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.user_type, self.user_data['user_type'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected)
    
    def test_user_properties(self):
        """Test user type properties."""
        teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass123',
            user_type='teacher'
        )
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            user_type='student'
        )
        
        self.assertTrue(teacher.is_teacher)
        self.assertFalse(teacher.is_student)
        self.assertTrue(student.is_student)
        self.assertFalse(student.is_teacher)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.get_full_name(), expected)


class UserAPITest(APITestCase):
    """Test cases for User API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.register_url = reverse('auth:register')
        self.login_url = reverse('auth:login')
        
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
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch."""
        self.user_data['password_confirm'] = 'wrongpassword'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email."""
        self.user_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Test successful user login."""
        # Create user first
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password(self):
        """Test changing user password."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        self.client.force_authenticate(user=user)
        
        change_password_data = {
            'old_password': self.user_data['password'],
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        change_password_url = reverse('auth:change_password')
        response = self.client.post(change_password_url, change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
    
    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        self.client.force_authenticate(user=user)
        
        change_password_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        change_password_url = reverse('auth:change_password')
        response = self.client.post(change_password_url, change_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout(self):
        """Test user logout."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            user_type=self.user_data['user_type']
        )
        self.client.force_authenticate(user=user)
        
        refresh = RefreshToken.for_user(user)
        logout_data = {'refresh_token': str(refresh)}
        logout_url = reverse('auth:logout')
        
        response = self.client.post(logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
