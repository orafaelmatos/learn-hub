from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLoginView, UserRegistrationView, change_password, logout

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change_password'),
    
]