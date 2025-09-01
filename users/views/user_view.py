from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsOwnerOrReadOnly

from ..repositories.user_repository import UserRepository
from ..serializers.user_serializer import (
    LoginSerializer,
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from ..services.auth_service import (
    authenticate_user,
    blacklist_refresh_token,
    change_user_password,
    generate_tokens_for_user,
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = generate_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_user(serializer.validated_data)

        tokens = generate_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    change_user_password(request.user, serializer.validated_data['new_password'])
    update_session_auth_hash(request, request.user)
    return Response({'message': 'Password changed successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh_token')
    blacklist_refresh_token(refresh_token)
    return Response({'message': 'Logged out successfully'})


class TeacherListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRepository.get_teachers()
