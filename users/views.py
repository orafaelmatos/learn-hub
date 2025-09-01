# from django.contrib.auth import update_session_auth_hash
# from rest_framework import generics, status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken

# from .models import User
# from .permissions import IsOwnerOrReadOnly
# from .serializers import (
#     LoginSerializer,
#     PasswordChangeSerializer,
#     UserCreateSerializer,
#     UserSerializer,
#     UserUpdateSerializer,
# )


# class UserRegistrationView(generics.CreateAPIView):
#     """
#     View for user registration.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     queryset = User.objects.all()
#     serializer_class = UserCreateSerializer
#     permission_classes = [AllowAny]
    
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
        
#         # Generate tokens
#         refresh = RefreshToken.for_user(user)
        
#         return Response({
#             'user': UserSerializer(user).data,
#             'tokens': {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#         }, status=status.HTTP_201_CREATED)


# class UserLoginView(generics.GenericAPIView):
#     """
#     View for user login.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
        
#         # Generate tokens
#         refresh = RefreshToken.for_user(user)
        
#         return Response({
#             'user': UserSerializer(user).data,
#             'tokens': {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#         })


# class UserProfileView(generics.RetrieveUpdateAPIView):
#     """
#     View for user profile management.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
#     def get_object(self):
#         return self.request.user


# class UserUpdateView(generics.UpdateAPIView):
#     """
#     View for updating user profile.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     serializer_class = UserUpdateSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self):
#         return self.request.user


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def change_password(request):
#     """
#     View for changing user password.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
#     serializer.is_valid(raise_exception=True)
    
#     user = request.user
#     user.set_password(serializer.validated_data['new_password'])
#     user.save()
    
#     # Update session to prevent logout
#     update_session_auth_hash(request, user)
    
#     return Response({'message': 'Password changed successfully'})


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     """
#     View for user logout.
#     """
#     try:
#         refresh_token = request.data.get('refresh_token')
#         if refresh_token:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#         return Response({'message': 'Logged out successfully'})
#     except Exception:
#         return Response({'message': 'Logged out successfully'})


# class TeacherListView(generics.ListAPIView):
#     """
#     View for listing teachers.
#     Following Dependency Inversion Principle - depends on abstractions (serializers).
#     """
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]
    
#     def get_queryset(self):
#         return User.objects.filter(user_type='teacher').order_by('id')