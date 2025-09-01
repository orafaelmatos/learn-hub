from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """
    Permission to check if user is a teacher.
    Following Interface Segregation Principle - specific permission for teachers.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher


class IsStudent(permissions.BasePermission):
    """
    Permission to check if user is a student.
    Following Interface Segregation Principle - specific permission for students.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin.
    Following Interface Segregation Principle - specific permission for admins.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owners to edit their own objects.
    Following Interface Segregation Principle - specific permission for object ownership.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        return obj.user == request.user


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Permission to allow teachers to edit, students to read only.
    Following Interface Segregation Principle - specific permission for teacher-student roles.
    """
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for teachers
        return request.user.is_authenticated and request.user.is_teacher 