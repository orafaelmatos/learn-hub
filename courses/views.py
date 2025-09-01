from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsTeacher, IsTeacherOrReadOnly

from .models import Category, Course, CourseEnrollment, CourseRating
from .serializers import (
    CategorySerializer,
    CourseCreateSerializer,
    CourseEnrollmentCreateSerializer,
    CourseEnrollmentSerializer,
    CourseRatingCreateSerializer,
    CourseRatingSerializer,
    CourseSerializer,
    CourseUpdateSerializer,
)


class CategoryListView(generics.ListCreateAPIView):
    """
    View for listing and creating categories.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for category details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CourseListView(generics.ListCreateAPIView):
    """
    View for listing and creating courses.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'teacher', 'difficulty', 'status']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['title', 'created_at', 'price', 'average_rating']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.all()
        # Filter by published courses for non-teachers
        if not self.request.user.is_teacher:
            queryset = queryset.filter(status='published')
        return queryset


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for course details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseUpdateSerializer
        return CourseSerializer


class TeacherCourseListView(generics.ListAPIView):
    """
    View for listing teacher's courses.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_course(request, course_id):
    """
    View for enrolling in a course.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        course = Course.objects.get(id=course_id, status='published')
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if course.is_full:
        return Response({'error': 'Course is full'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already enrolled
    if CourseEnrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create enrollment
    enrollment = CourseEnrollment.objects.create(student=request.user, course=course)
    
    # Update course student count
    course.current_students += 1
    course.save()
    
    serializer = CourseEnrollmentSerializer(enrollment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unenroll_course(request, course_id):
    """
    View for unenrolling from a course.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        enrollment = CourseEnrollment.objects.get(
            student=request.user, 
            course_id=course_id, 
            is_active=True
        )
    except CourseEnrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Deactivate enrollment
    enrollment.is_active = False
    enrollment.save()
    
    # Update course student count
    course = enrollment.course
    course.current_students = max(0, course.current_students - 1)
    course.save()
    
    return Response({'message': 'Successfully unenrolled'})


class CourseEnrollmentListView(generics.ListAPIView):
    """
    View for listing user enrollments.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(student=self.request.user, is_active=True).order_by('id')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_course(request, course_id):
    """
    View for rating a course.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is enrolled
    if not CourseEnrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        return Response({'error': 'Must be enrolled to rate'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already rated
    rating, created = CourseRating.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'rating': request.data.get('rating'), 'review': request.data.get('review', '')}
    )
    
    if not created:
        # Update existing rating
        rating.rating = request.data.get('rating', rating.rating)
        rating.review = request.data.get('review', rating.review)
        rating.save()
    
    # Update course average rating
    ratings = course.ratings.all()
    if ratings:
        course.average_rating = sum(r.rating for r in ratings) / len(ratings)
        course.total_ratings = len(ratings)
        course.save()
    
    serializer = CourseRatingSerializer(rating)
    return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CourseRatingListView(generics.ListAPIView):
    """
    View for listing course ratings.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = CourseRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return CourseRating.objects.filter(course_id=course_id) 