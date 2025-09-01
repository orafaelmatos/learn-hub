from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Category, Course, CourseEnrollment, CourseRating

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test cases for Category model."""
    
    def setUp(self):
        """Set up test data."""
        self.category_data = {
            'name': 'Programming',
            'description': 'Programming courses'
        }
    
    def test_create_category(self):
        """Test creating a new category."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, self.category_data['name'])
        self.assertEqual(category.description, self.category_data['description'])
    
    def test_category_str_representation(self):
        """Test category string representation."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), self.category_data['name'])


class CourseModelTest(TestCase):
    """Test cases for Course model."""
    
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
        
        self.course_data = {
            'title': 'Python Programming',
            'description': 'Learn Python programming',
            'short_description': 'Python basics',
            'category': self.category,
            'teacher': self.teacher,
            'difficulty': 'beginner',
            'duration_hours': 20,
            'price': Decimal('99.99'),
            'max_students': 50
        }
    
    def test_create_course(self):
        """Test creating a new course."""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(course.title, self.course_data['title'])
        self.assertEqual(course.teacher, self.teacher)
        self.assertEqual(course.category, self.category)
        self.assertEqual(course.status, 'draft')
    
    def test_course_str_representation(self):
        """Test course string representation."""
        course = Course.objects.create(**self.course_data)
        self.assertEqual(str(course), self.course_data['title'])
    
    def test_course_properties(self):
        """Test course properties."""
        course = Course.objects.create(**self.course_data)
        
        self.assertFalse(course.is_published)
        self.assertFalse(course.is_full)
        self.assertEqual(course.available_slots, 50)
        
        # Test when course is full
        course.current_students = 50
        course.save()
        self.assertTrue(course.is_full)
        self.assertEqual(course.available_slots, 0)
    
    def test_course_published_status(self):
        """Test course published status."""
        course = Course.objects.create(**self.course_data)
        course.status = 'published'
        course.save()
        self.assertTrue(course.is_published)


class CourseEnrollmentModelTest(TestCase):
    """Test cases for CourseEnrollment model."""
    
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
    
    def test_create_enrollment(self):
        """Test creating a new enrollment."""
        enrollment = CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertTrue(enrollment.is_active)
    
    def test_enrollment_str_representation(self):
        """Test enrollment string representation."""
        enrollment = CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        expected = f"{self.student.get_full_name()} - {self.course.title}"
        self.assertEqual(str(enrollment), expected)


class CourseRatingModelTest(TestCase):
    """Test cases for CourseRating model."""
    
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
    
    def test_create_rating(self):
        """Test creating a new rating."""
        rating = CourseRating.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review='Great course!'
        )
        self.assertEqual(rating.student, self.student)
        self.assertEqual(rating.course, self.course)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review, 'Great course!')
    
    def test_rating_str_representation(self):
        """Test rating string representation."""
        rating = CourseRating.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review='Great course!'
        )
        expected = f"{self.student.get_full_name()} - {self.course.title} (5/5)"
        self.assertEqual(str(rating), expected)


class CategoryAPITest(APITestCase):
    """Test cases for Category API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.category_list_url = reverse('courses:category_list')
        self.category_data = {
            'name': 'Programming',
            'description': 'Programming courses'
        }
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            user_type='student'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_category(self):
        """Test creating a new category."""
        response = self.client.post(self.category_list_url, self.category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.category_data['name'])
    
    def test_list_categories(self):
        """Test listing categories."""
        Category.objects.create(**self.category_data)
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_category_detail(self):
        """Test getting category details."""
        category = Category.objects.create(**self.category_data)
        url = reverse('courses:category_detail', kwargs={'pk': category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], category.name)
    
    def test_update_category(self):
        """Test updating a category."""
        category = Category.objects.create(**self.category_data)
        url = reverse('courses:category_detail', kwargs={'pk': category.pk})
        update_data = {'name': 'Updated Programming', 'description': 'Updated description'}
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Programming')
    
    def test_delete_category(self):
        """Test deleting a category."""
        category = Category.objects.create(**self.category_data)
        url = reverse('courses:category_detail', kwargs={'pk': category.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())


class CourseAPITest(APITestCase):
    """Test cases for Course API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.course_list_url = reverse('courses:course_list')
        
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
        
        self.course_data = {
            'title': 'Python Programming',
            'description': 'Learn Python programming',
            'short_description': 'Python basics',
            'category': self.category.id,
            'difficulty': 'beginner',
            'duration_hours': 20,
            'price': '99.99',
            'max_students': 50
        }
    
    def test_create_course_as_teacher(self):
        """Test creating a course as a teacher."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.course_list_url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.course_data['title'])
        self.assertEqual(response.data['teacher'], self.teacher.id)
    
    def test_create_course_as_student_forbidden(self):
        """Test that students cannot create courses."""
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.course_list_url, self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_courses(self):
        """Test listing courses."""
        course = Course.objects.create(
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
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_course_detail(self):
        """Test getting course details."""
        course = Course.objects.create(
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
        
        url = reverse('courses:course_detail', kwargs={'pk': course.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], course.title)
    
    def test_update_course_as_teacher(self):
        """Test updating a course as the teacher."""
        course = Course.objects.create(
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
        
        url = reverse('courses:course_detail', kwargs={'pk': course.pk})
        self.client.force_authenticate(user=self.teacher)
        update_data = {'title': 'Updated Python Course', 'description': 'Updated description'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Python Course')
    
    def test_enroll_in_course(self):
        """Test enrolling in a course."""
        course = Course.objects.create(
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
        
        url = reverse('courses:enroll_course', kwargs={'course_id': course.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if enrollment was created
        self.assertTrue(CourseEnrollment.objects.filter(student=self.student, course=course).exists())
        
        # Check if course student count was updated
        course.refresh_from_db()
        self.assertEqual(course.current_students, 1)
    
    def test_enroll_in_full_course(self):
        """Test enrolling in a full course."""
        course = Course.objects.create(
            title='Python Programming',
            description='Learn Python programming',
            short_description='Python basics',
            category=self.category,
            teacher=self.teacher,
            difficulty='beginner',
            duration_hours=20,
            price=Decimal('99.99'),
            max_students=1,
            current_students=1,
            status='published'
        )
        
        url = reverse('courses:enroll_course', kwargs={'course_id': course.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_rate_course(self):
        """Test rating a course."""
        course = Course.objects.create(
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
        
        # Enroll student first
        CourseEnrollment.objects.create(student=self.student, course=course)
        
        url = reverse('courses:rate_course', kwargs={'course_id': course.pk})
        self.client.force_authenticate(user=self.student)
        rating_data = {'rating': 5, 'review': 'Great course!'}
        response = self.client.post(url, rating_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if rating was created
        self.assertTrue(CourseRating.objects.filter(student=self.student, course=course).exists())
        
        # Check if course average rating was updated
        course.refresh_from_db()
        self.assertEqual(course.average_rating, Decimal('5.00'))
        self.assertEqual(course.total_ratings, 1)
    
    def test_rate_course_not_enrolled(self):
        """Test rating a course without being enrolled."""
        course = Course.objects.create(
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
        
        url = reverse('courses:rate_course', kwargs={'course_id': course.pk})
        self.client.force_authenticate(user=self.student)
        rating_data = {'rating': 5, 'review': 'Great course!'}
        response = self.client.post(url, rating_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseEnrollmentAPITest(APITestCase):
    """Test cases for CourseEnrollment API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.enrollment_list_url = reverse('courses:enrollment_list')
        
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
    
    def test_list_enrollments(self):
        """Test listing user enrollments."""
        enrollment = CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.enrollment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['course'], self.course.id)
    
    def test_unenroll_from_course(self):
        """Test unenrolling from a course."""
        enrollment = CourseEnrollment.objects.create(
            student=self.student,
            course=self.course
        )
        
        # Update course student count
        self.course.current_students = 1
        self.course.save()
        
        url = reverse('courses:unenroll_course', kwargs={'course_id': self.course.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if enrollment was deactivated
        enrollment.refresh_from_db()
        self.assertFalse(enrollment.is_active)
        
        # Check if course student count was updated
        self.course.refresh_from_db()
        self.assertEqual(self.course.current_students, 0) 