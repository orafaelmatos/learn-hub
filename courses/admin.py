from django.contrib import admin

from .models import Category, Course, CourseEnrollment, CourseRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    """
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Course model.
    """
    list_display = ('title', 'teacher', 'category', 'difficulty', 'status', 'price', 'current_students', 'average_rating', 'created_at')
    list_filter = ('category', 'difficulty', 'status', 'created_at')
    search_fields = ('title', 'description', 'teacher__email', 'teacher__first_name', 'teacher__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('current_students', 'average_rating', 'total_ratings', 'created_at', 'updated_at', 'published_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'short_description', 'thumbnail')
        }),
        ('Course Details', {
            'fields': ('category', 'teacher', 'difficulty', 'status')
        }),
        ('Course Metadata', {
            'fields': ('duration_hours', 'price', 'max_students', 'current_students')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_ratings')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for CourseEnrollment model.
    """
    list_display = ('student', 'course', 'enrolled_at', 'completed_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at', 'completed_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'course__title')
    ordering = ('-enrolled_at',)
    readonly_fields = ('enrolled_at',)


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    """
    Admin configuration for CourseRating model.
    """
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'course__title', 'review')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at') 