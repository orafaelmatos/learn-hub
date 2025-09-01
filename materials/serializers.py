from rest_framework import serializers

from .models import Material, MaterialAccess, MaterialFolder


class MaterialFolderSerializer(serializers.ModelSerializer):
    """
    Material folder serializer following Open/Closed Principle.
    """
    materials_count = serializers.ReadOnlyField()
    subfolders_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaterialFolder
        fields = [
            'id', 'name', 'description', 'course', 'parent_folder',
            'materials_count', 'subfolders_count', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaterialFolderCreateSerializer(serializers.ModelSerializer):
    """
    Material folder creation serializer following Open/Closed Principle.
    """
    created_by = serializers.ReadOnlyField(source='created_by.id')
    
    class Meta:
        model = MaterialFolder
        fields = ['name', 'description', 'course', 'parent_folder', 'created_by']
        read_only_fields = ['created_by']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MaterialSerializer(serializers.ModelSerializer):
    """
    Material serializer following Open/Closed Principle.
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    download_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Material
        fields = [
            'id', 'title', 'description', 'material_type', 'file',
            'file_size', 'file_size_mb', 'file_extension', 'course', 'course_title',
            'teacher', 'teacher_name', 'folder', 'folder_name', 'is_public',
            'is_downloadable', 'download_count', 'view_count', 'download_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'file_extension', 'download_count', 'view_count',
            'created_at', 'updated_at'
        ]


class MaterialCreateSerializer(serializers.ModelSerializer):
    """
    Material creation serializer following Open/Closed Principle.
    """
    teacher = serializers.ReadOnlyField(source='teacher.id')
    
    class Meta:
        model = Material
        fields = [
            'title', 'description', 'material_type', 'file', 'course',
            'folder', 'is_public', 'is_downloadable', 'teacher'
        ]
        read_only_fields = ['teacher']
    
    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class MaterialUpdateSerializer(serializers.ModelSerializer):
    """
    Material update serializer following Open/Closed Principle.
    """
    
    class Meta:
        model = Material
        fields = [
            'title', 'description', 'material_type', 'file', 'folder',
            'is_public', 'is_downloadable'
        ]


class MaterialAccessSerializer(serializers.ModelSerializer):
    """
    Material access serializer following Open/Closed Principle.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    material_title = serializers.CharField(source='material.title', read_only=True)
    
    class Meta:
        model = MaterialAccess
        fields = [
            'id', 'student', 'student_name', 'material', 'material_title',
            'action', 'accessed_at'
        ]
        read_only_fields = ['id', 'accessed_at']


class MaterialDownloadSerializer(serializers.Serializer):
    """
    Material download serializer following Open/Closed Principle.
    """
    material_id = serializers.IntegerField()
    
    def validate_material_id(self, value):
        try:
            Material.objects.get(id=value)
        except Material.DoesNotExist:
            raise serializers.ValidationError("Material does not exist.")
        return value


class MaterialViewSerializer(serializers.Serializer):
    """
    Material view serializer following Open/Closed Principle.
    """
    material_id = serializers.IntegerField()
    
    def validate_material_id(self, value):
        try:
            Material.objects.get(id=value)
        except Material.DoesNotExist:
            raise serializers.ValidationError("Material does not exist.")
        return value 