from django.urls import path

from .views.user_view import TeacherListView, UserProfileView, UserUpdateView

app_name = 'users'

urlpatterns = [    
    # User management endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path('teachers/', TeacherListView.as_view(), name='teachers_list'),
] 