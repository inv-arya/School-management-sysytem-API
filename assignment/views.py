# assignment/views.py
import magic
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Assignment
from .serializers import AssignmentSerializer
from datetime import datetime

class AssignmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'teacher':
            return Response({"error": "Only teachers can create assignments"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['created_by'] = request.user.teacher.id
        
        # Validate deadline
        try:
            deadline = datetime.fromisoformat(data['deadline'])
            if deadline < datetime.now():
                return Response({"error": "Deadline must be in the future"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid deadline format"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
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
            file.seek(0)  # Reset file pointer
        
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


