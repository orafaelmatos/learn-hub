from rest_framework import serializers

from .models import Category, Course, CourseEnrollment, CourseRating


class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """
    Course serializer following Open/Closed Principle.
    """
    category = CategorySerializer(read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'short_description', 'thumbnail',
            'category', 'teacher', 'teacher_name', 'difficulty', 'status',
            'duration_hours', 'price', 'max_students', 'current_students',
            'average_rating', 'total_ratings', 'enrollment_count',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'current_students', 'average_rating', 'total_ratings',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()


class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Course creation serializer following Open/Closed Principle.
    """
    teacher = serializers.ReadOnlyField(source='teacher.id')
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'thumbnail',
            'category', 'difficulty', 'duration_hours', 'price', 'max_students', 'teacher'
        ]
        read_only_fields = ['teacher']
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class CourseUpdateSerializer(serializers.ModelSerializer):
    """
    Course update serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'thumbnail',
            'category', 'difficulty', 'status', 'duration_hours', 'price', 'max_students'
        ]


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """
    Course enrollment serializer following Open/Closed Principle.
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'student', 'course', 'course_title', 'student_name',
            'enrolled_at', 'completed_at', 'is_active'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at']


class CourseEnrollmentCreateSerializer(serializers.ModelSerializer):
    """
    Course enrollment creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = CourseEnrollment
        fields = ['course']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class CourseRatingSerializer(serializers.ModelSerializer):
    """
    Course rating serializer following Open/Closed Principle.
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = CourseRating
        fields = [
            'id', 'student', 'course', 'course_title', 'student_name',
            'rating', 'review', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseRatingCreateSerializer(serializers.ModelSerializer):
    """
    Course rating creation serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = CourseRating
        fields = ['course', 'rating', 'review']
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data) 