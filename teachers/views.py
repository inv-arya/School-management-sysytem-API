# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Teacher
# from .serializers import TeacherSerializer
# from students.serializers import StudentSerializer

# class TeacherViewSet(viewsets.ModelViewSet):  # ✅ Use only this
#     queryset = Teacher.objects.all()
#     serializer_class = TeacherSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=True, methods=['get'])
#     def students(self, request, pk=None):
#         teacher = self.get_object()
#         students = teacher.students.all()
#         serializer = StudentSerializer(students, many=True)
#         return Response(serializer.data)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def perform_create(self, serializer):
#         serializer.save()

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Teacher
from .serializers import TeacherSerializer
from accounts.permissions import TeacherAccessPermission
from rest_framework.permissions import IsAuthenticated

class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminUser]  # Only admins can create/list teachers

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    # permission_classes = [IsAdminUser]  # Only admins can edit/delete teachers
    permission_classes = [IsAuthenticated, TeacherAccessPermission]
