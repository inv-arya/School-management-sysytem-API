from rest_framework.permissions import BasePermission, SAFE_METHODS

class StudentAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'teacher':
            return obj.assigned_teacher and obj.assigned_teacher.user == user
        if user.role == 'student':
            return obj.user == user and request.method in SAFE_METHODS
        return False
        
class TeacherAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'teacher':
            return obj.user == user and request.method in SAFE_METHODS
        return False