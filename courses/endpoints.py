from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListView,
    CourseDetailView,
    CourseEnrollmentListView,
    CourseListView,
    CourseRatingListView,
    TeacherCourseListView,
    enroll_course,
    rate_course,
    unenroll_course,
)

app_name = 'courses'

urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Course endpoints
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/teacher/', TeacherCourseListView.as_view(), name='teacher_courses'),
    
    # Enrollment endpoints
    path('courses/<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/unenroll/', unenroll_course, name='unenroll_course'),
    path('enrollments/', CourseEnrollmentListView.as_view(), name='enrollment_list'),
    
    # Rating endpoints
    path('courses/<int:course_id>/rate/', rate_course, name='rate_course'),
    path('courses/<int:course_id>/ratings/', CourseRatingListView.as_view(), name='course_ratings'),
] 