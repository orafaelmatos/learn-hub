from django.core.validators import FileExtensionValidator
from django.db import models

from courses.models import Course
from users.models.user_model import User


class Material(models.Model):
    """
    Material model following Single Responsibility Principle.
    Responsible only for material information and file management.
    """
    MATERIAL_TYPE_CHOICES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('presentation', 'Presentation'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='document')
    
    # File information
    file = models.FileField(
        upload_to='materials/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'mp4', 'avi', 'mov', 
                                  'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'zip', 'rar']
            )
        ]
    )
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    file_extension = models.CharField(max_length=10, blank=True)
    
    # Relationships
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materials_created')
    folder = models.ForeignKey('MaterialFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
    
    # Access control
    is_public = models.BooleanField(default=False, help_text='Available to all enrolled students')
    is_downloadable = models.BooleanField(default=True, help_text='Students can download this material')
    
    # Metadata
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # Set file size and extension on save
        if self.file:
            self.file_size = self.file.size
            self.file_extension = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Get file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def download_url(self):
        """Get download URL if downloadable."""
        if self.is_downloadable:
            return self.file.url
        return None


class MaterialAccess(models.Model):
    """
    Material access model following Single Responsibility Principle.
    Responsible only for tracking material access by students.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='material_accesses')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='accesses')
    accessed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('download', 'Download'),
    ])
    
    class Meta:
        db_table = 'material_accesses'
        verbose_name = 'Material Access'
        verbose_name_plural = 'Material Accesses'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.material.title} ({self.action})"


class MaterialFolder(models.Model):
    """
    Material folder model following Single Responsibility Principle.
    Responsible only for organizing materials in folders.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='material_folders')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'material_folders'
        verbose_name = 'Material Folder'
        verbose_name_plural = 'Material Folders'
        unique_together = ['name', 'course', 'parent_folder']
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"
    
    @property
    def materials_count(self):
        """Get number of materials in this folder."""
        return self.materials.count()
    
    @property
    def subfolders_count(self):
        """Get number of subfolders."""
        return self.subfolders.count() 