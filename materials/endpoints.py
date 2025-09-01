from django.urls import path

from .views import (
    MaterialAccessListView,
    MaterialDetailView,
    MaterialFolderDetailView,
    MaterialFolderListView,
    MaterialListView,
    TeacherMaterialListView,
    download_material,
    material_stats,
    view_material,
)

app_name = 'materials'

urlpatterns = [
    # Material folder endpoints
    path('folders/', MaterialFolderListView.as_view(), name='folder_list'),
    path('folders/<int:pk>/', MaterialFolderDetailView.as_view(), name='folder_detail'),
    
    # Material endpoints
    path('materials/', MaterialListView.as_view(), name='material_list'),
    path('materials/<int:pk>/', MaterialDetailView.as_view(), name='material_detail'),
    path('materials/teacher/', TeacherMaterialListView.as_view(), name='teacher_materials'),
    
    # Material access endpoints
    path('materials/<int:material_id>/download/', download_material, name='download_material'),
    path('materials/<int:material_id>/view/', view_material, name='view_material'),
    path('materials/<int:material_id>/stats/', material_stats, name='material_stats'),
    path('accesses/', MaterialAccessListView.as_view(), name='access_list'),
] 