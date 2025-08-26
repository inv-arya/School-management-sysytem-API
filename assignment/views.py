import magic
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Assignment
from .serializers import AssignmentSerializer
from datetime import datetime
from django.utils import timezone

class AssignmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user=self.request.user
        print(user.role)
        if user.role != 'teacher':
            return Response({"error": "Only teachers can create assignments"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['created_by'] = user.teacher.id
        
        
        try:
            deadline = datetime.fromisoformat(data['deadline'])
            if deadline < datetime.now():
                return Response({"error": "Deadline must be in the future"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid deadline format"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if 'reference_files' in request.FILES:
            file = request.FILES['reference_files']
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read())
            allowed_types = [
                'application/pdf',
                'image/jpeg', 'image/png',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.ms-powerpoint',
            ]
            if file_type not in allowed_types:
                return Response({"error": f"Invalid file type: {file_type}"}, status=status.HTTP_400_BAD_REQUEST)
            file.seek(0)  
        
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(created_by=user.teacher)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'teacher':
            return Response({"error": "Only teachers can view their assignments"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            teacher = request.user.teacher
        except AttributeError:
            return Response({"error": "User is not associated with a Teacher profile"}, status=status.HTTP_400_BAD_REQUEST)
        
        assignments = Assignment.objects.filter(created_by=teacher)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignmentDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()

    def get_object(self):
        try:
            assignment = Assignment.objects.get(pk=self.kwargs['pk'])
        except Assignment.DoesNotExist:
            return None
        
        
        if self.request.user.role != 'teacher':
            return None
        if assignment.created_by != self.request.user.teacher:
            return None
        return assignment

    def validate_request(self, data, files):
        
        
        if "deadline" in data:
            try:
                deadline = datetime.fromisoformat(data["deadline"])
                if timezone.is_naive(deadline):   
                    deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
                if deadline < timezone.now():
                    return {"error": "Deadline must be in the future"}
            except ValueError:
                return {"error": "Invalid deadline format"}

        
        if "reference_files" in files:
            file = files["reference_files"]
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read())
            allowed_types = [
                "application/pdf",
                "image/jpeg", "image/png",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.ms-powerpoint",
            ]
            if file_type not in allowed_types:
                return {"error": f"Invalid file type: {file_type}"}
            file.seek(0)

        return None

    def put(self, request, pk):
        
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        if assignment.deadline < timezone.now():
            return Response({"error": "Assignment deadline has passed. Editing not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        error = self.validate_request(request.data, request.FILES)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(assignment, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        if assignment.deadline < timezone.now():
            return Response({"error": "Assignment deadline has passed. Editing not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        error = self.validate_request(request.data, request.FILES)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        assignment = self.get_object()
        if not assignment:
            return Response({"error": "Not authorized or Assignment not found"}, status=status.HTTP_404_NOT_FOUND)

        assignment.delete()
        return Response({"message": "Assignment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)