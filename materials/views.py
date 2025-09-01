from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import CourseEnrollment
from users.permissions import IsTeacher, IsTeacherOrReadOnly

from .models import Material, MaterialAccess, MaterialFolder
from .serializers import (
    MaterialAccessSerializer,
    MaterialCreateSerializer,
    MaterialDownloadSerializer,
    MaterialFolderCreateSerializer,
    MaterialFolderSerializer,
    MaterialSerializer,
    MaterialUpdateSerializer,
    MaterialViewSerializer,
)


class MaterialFolderListView(generics.ListCreateAPIView):
    """
    View for listing and creating material folders.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = MaterialFolder.objects.all().order_by('id')
    serializer_class = MaterialFolderSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MaterialFolderCreateSerializer
        return MaterialFolderSerializer
    
    def get_queryset(self):
        queryset = MaterialFolder.objects.all().order_by('id')
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class MaterialFolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for material folder details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = MaterialFolder.objects.all()
    serializer_class = MaterialFolderSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]


class MaterialListView(generics.ListCreateAPIView):
    """
    View for listing and creating materials.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'teacher', 'material_type', 'is_public', 'is_downloadable']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'download_count', 'view_count']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MaterialCreateSerializer
        return MaterialSerializer
    
    def get_queryset(self):
        queryset = Material.objects.all()
        user = self.request.user
        
        # Teachers can see all materials they created
        if user.is_teacher:
            return queryset.filter(teacher=user)
        
        # Students can only see materials from courses they're enrolled in
        enrolled_courses = CourseEnrollment.objects.filter(
            student=user, is_active=True
        ).values_list('course_id', flat=True)
        return queryset.filter(course_id__in=enrolled_courses)


class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for material details.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MaterialUpdateSerializer
        return MaterialSerializer


class TeacherMaterialListView(generics.ListAPIView):
    """
    View for listing teacher's materials.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return Material.objects.filter(teacher=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_material(request, material_id):
    """
    View for downloading materials.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        material = Material.objects.get(id=material_id)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can access this material
    if not material.is_downloadable:
        return Response({'error': 'Material is not downloadable'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if user is enrolled in the course or is the teacher
    if not (request.user.is_teacher and material.teacher == request.user):
        if not CourseEnrollment.objects.filter(
            student=request.user, 
            course=material.course, 
            is_active=True
        ).exists():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Record download access
    MaterialAccess.objects.create(
        student=request.user,
        material=material,
        action='download'
    )
    
    # Update download count
    material.download_count += 1
    material.save()
    
    # Return file for download
    try:
        response = FileResponse(material.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{material.file.name.split("/")[-1]}"'
        return response
    except FileNotFoundError:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def view_material(request, material_id):
    """
    View for recording material view.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        material = Material.objects.get(id=material_id)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can access this material
    if not (request.user.is_teacher and material.teacher == request.user):
        if not CourseEnrollment.objects.filter(
            student=request.user, 
            course=material.course, 
            is_active=True
        ).exists():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Record view access
    MaterialAccess.objects.create(
        student=request.user,
        material=material,
        action='view'
    )
    
    # Update view count
    material.view_count += 1
    material.save()
    
    return Response({'message': 'View recorded successfully'})


class MaterialAccessListView(generics.ListAPIView):
    """
    View for listing material access records.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    serializer_class = MaterialAccessSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return MaterialAccess.objects.filter(material__teacher=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def material_stats(request, material_id):
    """
    View for getting material statistics.
    Following Dependency Inversion Principle - depends on abstractions (serializers).
    """
    try:
        material = Material.objects.get(id=material_id)
    except Material.DoesNotExist:
        return Response({'error': 'Material not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Only teachers can see stats for their materials
    if not (request.user.is_teacher and material.teacher == request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get access statistics
    view_count = MaterialAccess.objects.filter(material=material, action='view').count()
    download_count = MaterialAccess.objects.filter(material=material, action='download').count()
    
    # Get recent accesses
    recent_accesses = MaterialAccess.objects.filter(material=material).order_by('-accessed_at')[:10]
    recent_accesses_data = MaterialAccessSerializer(recent_accesses, many=True).data
    
    return Response({
        'material_id': material.id,
        'title': material.title,
        'view_count': view_count,
        'download_count': download_count,
        'recent_accesses': recent_accesses_data
    }) 