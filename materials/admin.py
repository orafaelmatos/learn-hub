from django.contrib import admin

from .models import Material, MaterialAccess, MaterialFolder


@admin.register(MaterialFolder)
class MaterialFolderAdmin(admin.ModelAdmin):
    """
    Admin configuration for MaterialFolder model.
    """
    list_display = ('name', 'course', 'parent_folder', 'created_by', 'materials_count', 'subfolders_count', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('name', 'description', 'course__title', 'created_by__email')
    ordering = ('-created_at',)
    readonly_fields = ('materials_count', 'subfolders_count', 'created_at', 'updated_at')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Admin configuration for Material model.
    """
    list_display = ('title', 'course', 'teacher', 'material_type', 'file_size_mb', 'is_public', 'is_downloadable', 'download_count', 'view_count', 'created_at')
    list_filter = ('material_type', 'is_public', 'is_downloadable', 'created_at')
    search_fields = ('title', 'description', 'course__title', 'teacher__email', 'teacher__first_name', 'teacher__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'file_extension', 'download_count', 'view_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'material_type')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'file_extension')
        }),
        ('Relationships', {
            'fields': ('course', 'teacher', 'folder')
        }),
        ('Access Control', {
            'fields': ('is_public', 'is_downloadable')
        }),
        ('Statistics', {
            'fields': ('download_count', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaterialAccess)
class MaterialAccessAdmin(admin.ModelAdmin):
    """
    Admin configuration for MaterialAccess model.
    """
    list_display = ('student', 'material', 'action', 'accessed_at')
    list_filter = ('action', 'accessed_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'material__title')
    ordering = ('-accessed_at',)
    readonly_fields = ('accessed_at',) 