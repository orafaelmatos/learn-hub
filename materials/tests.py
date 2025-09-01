import gc
import os
import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from courses.models import Category, Course, CourseEnrollment

from .models import Material, MaterialAccess, MaterialFolder

User = get_user_model()


class MaterialFolderModelTest(TestCase):
    """Test cases for MaterialFolder model."""
    
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
        
        self.folder_data = {
            'name': 'Lecture Notes',
            'description': 'Course lecture notes',
            'course': self.course,
            'created_by': self.teacher
        }
    
    def test_create_folder(self):
        """Test creating a new folder."""
        folder = MaterialFolder.objects.create(**self.folder_data)
        self.assertEqual(folder.name, self.folder_data['name'])
        self.assertEqual(folder.course, self.course)
        self.assertEqual(folder.created_by, self.teacher)
    
    def test_folder_str_representation(self):
        """Test folder string representation."""
        folder = MaterialFolder.objects.create(**self.folder_data)
        expected = f"{folder.name} - {self.course.title}"
        self.assertEqual(str(folder), expected)
    
    def test_folder_properties(self):
        """Test folder properties."""
        folder = MaterialFolder.objects.create(**self.folder_data)
        
        # Create a subfolder
        subfolder = MaterialFolder.objects.create(
            name='Subfolder',
            description='Subfolder description',
            course=self.course,
            parent_folder=folder,
            created_by=self.teacher
        )
        
        self.assertEqual(folder.subfolders_count, 1)
        self.assertEqual(folder.materials_count, 0)


class MaterialModelTest(TestCase):
    """Test cases for Material model."""
    
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
        
        self.folder = MaterialFolder.objects.create(
            name='Lecture Notes',
            description='Course lecture notes',
            course=self.course,
            created_by=self.teacher
        )
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.temp_file.write(b'Test PDF content')
        self.temp_file.close()
        
        self.material_data = {
            'title': 'Lecture 1 - Introduction',
            'description': 'Introduction to Python programming',
            'material_type': 'document',
            'course': self.course,
            'teacher': self.teacher,
            'folder': self.folder,
            'is_public': True,
            'is_downloadable': True
        }
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        materials_dir = os.path.join('media', 'materials')
        if os.path.exists(materials_dir):
            shutil.rmtree(materials_dir)
        super().tearDown()
    
    def test_create_material(self):
        """Test creating a new material."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                file=SimpleUploadedFile('test.pdf', file.read()),
                **self.material_data
            )
        
        self.assertEqual(material.title, self.material_data['title'])
        self.assertEqual(material.course, self.course)
        self.assertEqual(material.teacher, self.teacher)
        self.assertEqual(material.material_type, 'document')
    
    def test_material_str_representation(self):
        """Test material string representation."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                file=SimpleUploadedFile('test.pdf', file.read()),
                **self.material_data
            )
        
        expected = f"{material.title} - {self.course.title}"
        self.assertEqual(str(material), expected)
    
    def test_material_properties(self):
        """Test material properties."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                file=SimpleUploadedFile('test.pdf', file.read()),
                **self.material_data
            )
        
        self.assertIsNotNone(material.file_size_mb)
        self.assertIsNotNone(material.download_url)
        
        # Test when material is not downloadable
        material.is_downloadable = False
        material.save()
        self.assertIsNone(material.download_url)


class MaterialAccessModelTest(TestCase):
    """Test cases for MaterialAccess model."""
    
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
        
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.temp_file.write(b'Test PDF content')
        self.temp_file.close()
        
        with open(self.temp_file.name, 'rb') as file:
            self.material = Material.objects.create(
                title='Lecture 1 - Introduction',
                description='Introduction to Python programming',
                material_type='document',
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                is_public=True,
                is_downloadable=True
            )
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        materials_dir = os.path.join('media', 'materials')
        if os.path.exists(materials_dir):
            shutil.rmtree(materials_dir)
        super().tearDown()
    
    def test_create_material_access(self):
        """Test creating a new material access record."""
        access = MaterialAccess.objects.create(
            student=self.student,
            material=self.material,
            action='view'
        )
        self.assertEqual(access.student, self.student)
        self.assertEqual(access.material, self.material)
        self.assertEqual(access.action, 'view')
    
    def test_material_access_str_representation(self):
        """Test material access string representation."""
        access = MaterialAccess.objects.create(
            student=self.student,
            material=self.material,
            action='download'
        )
        expected = f"{self.student.get_full_name()} - {self.material.title} (download)"
        self.assertEqual(str(access), expected)


class MaterialFolderAPITest(APITestCase):
    """Test cases for MaterialFolder API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.folder_list_url = reverse('materials:folder_list')
        
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
        
        self.folder_data = {
            'name': 'Lecture Notes',
            'description': 'Course lecture notes',
            'course': self.course.id,
            'parent_folder': None,
        }
        
        self.client.force_authenticate(user=self.teacher)
    
    def test_create_folder(self):
        """Test creating a new folder."""
        response = self.client.post(self.folder_list_url, self.folder_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.folder_data['name'])
        self.assertEqual(response.data['created_by'], self.teacher.id)
    
    def test_list_folders(self):
        """Test listing folders."""
        MaterialFolder.objects.create(
            name=self.folder_data['name'],
            description=self.folder_data['description'],
            course=self.course,
            created_by=self.teacher
        )
        
        response = self.client.get(self.folder_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_folder_detail(self):
        """Test getting folder details."""
        folder = MaterialFolder.objects.create(
            name=self.folder_data['name'],
            description=self.folder_data['description'],
            course=self.course,
            created_by=self.teacher
        )
        
        url = reverse('materials:folder_detail', kwargs={'pk': folder.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], folder.name)
    
    def test_update_folder(self):
        """Test updating a folder."""
        folder = MaterialFolder.objects.create(
            name=self.folder_data['name'],
            description=self.folder_data['description'],
            course=self.course,
            created_by=self.teacher,
            parent_folder=None
        )
        
        url = reverse('materials:folder_detail', kwargs={'pk': folder.pk})
        update_data = {
                'name': 'Updated Notes',
                'description': 'Updated description',
                'course': self.course.id,
                'parent_folder': None 
            }        
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Notes')
    
    def test_delete_folder(self):
        """Test deleting a folder."""
        folder = MaterialFolder.objects.create(
            name=self.folder_data['name'],
            description=self.folder_data['description'],
            course=self.course,
            created_by=self.teacher
        )
        
        url = reverse('materials:folder_detail', kwargs={'pk': folder.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MaterialFolder.objects.filter(pk=folder.pk).exists())


class MaterialAPITest(APITestCase):
    """Test cases for Material API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.material_list_url = reverse('materials:material_list')
        
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
        
        self.folder = MaterialFolder.objects.create(
            name='Lecture Notes',
            description='Course lecture notes',
            course=self.course,
            created_by=self.teacher
        )
        
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.temp_file.write(b'Test PDF content')
        self.temp_file.close()
        
        self.material_data = {
            'title': 'Lecture 1 - Introduction',
            'description': 'Introduction to Python programming',
            'material_type': 'document',
            'course': self.course.id,
            'folder': self.folder.id,
            'is_public': True,
            'is_downloadable': True
        }
    
    def tearDown(self):
        """Clean up temporary files."""
        for material in Material.objects.all():
            if material.file and not material.file.closed:
                material.file.close()
        gc.collect()
        try:
            if os.path.exists(self.temp_file.name):
                os.unlink(self.temp_file.name)
        except PermissionError:
            pass

        materials_dir = os.path.join('media', 'materials')
        if os.path.exists(materials_dir):
            shutil.rmtree(materials_dir, ignore_errors=True)
        super().tearDown()
    
    def test_create_material_as_teacher(self):
        """Test creating a material as a teacher."""
        self.client.force_authenticate(user=self.teacher)
        
        with open(self.temp_file.name, 'rb') as file:
            self.material_data['file'] = file
            response = self.client.post(self.material_list_url, self.material_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.material_data['title'])
        self.assertEqual(response.data['teacher'], self.teacher.id)
    
    def test_create_material_as_student_forbidden(self):
        """Test that students cannot create materials."""
        self.client.force_authenticate(user=self.student)
        
        with open(self.temp_file.name, 'rb') as file:
            self.material_data['file'] = file
            response = self.client.post(self.material_list_url, self.material_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_materials_as_teacher(self):
        """Test listing materials as a teacher."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                title=self.material_data['title'],
                description=self.material_data['description'],
                material_type=self.material_data['material_type'],
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                folder=self.folder,
                is_public=self.material_data['is_public'],
                is_downloadable=self.material_data['is_downloadable']
            )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.material_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_materials_as_student(self):
        """Test listing materials as a student."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                title=self.material_data['title'],
                description=self.material_data['description'],
                material_type=self.material_data['material_type'],
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                folder=self.folder,
                is_public=self.material_data['is_public'],
                is_downloadable=self.material_data['is_downloadable']
            )
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.material_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_material_detail(self):
        """Test getting material details."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                title=self.material_data['title'],
                description=self.material_data['description'],
                material_type=self.material_data['material_type'],
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                folder=self.folder,
                is_public=self.material_data['is_public'],
                is_downloadable=self.material_data['is_downloadable']
            )
        
        url = reverse('materials:material_detail', kwargs={'pk': material.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], material.title)
    
    def test_download_material(self):
        """Test downloading a material."""
        with open(self.temp_file.name, 'rb') as file:
            file_content = file.read()

        uploaded_file = SimpleUploadedFile('test.pdf', file_content)

        material = Material.objects.create(
            title=self.material_data['title'],
            description=self.material_data['description'],
            material_type=self.material_data['material_type'],
            file=uploaded_file,
            course=self.course,
            teacher=self.teacher,
            folder=self.folder,
            is_public=self.material_data['is_public'],
            is_downloadable=self.material_data['is_downloadable']
        )
        
        url = reverse('materials:download_material', kwargs={'material_id': material.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if access was recorded
        self.assertTrue(MaterialAccess.objects.filter(
            student=self.student,
            material=material,
            action='download'
        ).exists())
        
        # Check if download count was updated
        material.refresh_from_db()
        self.assertEqual(material.download_count, 1)
    
    def test_view_material(self):
        """Test viewing a material."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                title=self.material_data['title'],
                description=self.material_data['description'],
                material_type=self.material_data['material_type'],
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                folder=self.folder,
                is_public=self.material_data['is_public'],
                is_downloadable=self.material_data['is_downloadable']
            )
        
        url = reverse('materials:view_material', kwargs={'material_id': material.pk})
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if access was recorded
        self.assertTrue(MaterialAccess.objects.filter(
            student=self.student,
            material=material,
            action='view'
        ).exists())
        
        # Check if view count was updated
        material.refresh_from_db()
        self.assertEqual(material.view_count, 1)
    
    def test_material_stats(self):
        """Test getting material statistics."""
        with open(self.temp_file.name, 'rb') as file:
            material = Material.objects.create(
                title=self.material_data['title'],
                description=self.material_data['description'],
                material_type=self.material_data['material_type'],
                file=SimpleUploadedFile('test.pdf', file.read()),
                course=self.course,
                teacher=self.teacher,
                folder=self.folder,
                is_public=self.material_data['is_public'],
                is_downloadable=self.material_data['is_downloadable']
            )
        
        # Create some access records
        MaterialAccess.objects.create(
            student=self.student,
            material=material,
            action='view'
        )
        MaterialAccess.objects.create(
            student=self.student,
            material=material,
            action='download'
        )
        
        url = reverse('materials:material_stats', kwargs={'material_id': material.pk})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], 1)
        self.assertEqual(response.data['download_count'], 1) 