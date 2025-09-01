from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.services.change_password_service import ChangePasswordService
from auth.services.login_user_service import LoginUserService
from auth.services.logout_user_service import LogoutUserService
from auth.services.register_user_service import RegisterUserService

from .serializers.auth_serializer import LoginSerializer, UserCreateSerializer


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service = RegisterUserService()
        user, tokens = service.execute(request.data)
        return Response({
            'user': UserCreateSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service = LoginUserService()
        user, tokens = service.execute(request.data)
        return Response({
            'user': LoginSerializer(user).data,
            'tokens': tokens
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    service = ChangePasswordService()
    service.execute(request.user, request.data, request)
    return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh_token')
    service = LogoutUserService()
    service.execute(refresh_token)
    return Response({'message': 'Logged out successfully'})
