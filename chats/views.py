from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRequest, ChatMessage
from teachers.models import Teacher
from students.models import Student
from .serializers import ChatRequestCreateSerializer, ChatMessageSerializer,ChatRequestSerializer,ChatStatusSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone


class ChatRequestApproveView(generics.UpdateAPIView):
    queryset = ChatRequest.objects.all()
    permission_classes = []
    serializer_class = ChatRequestSerializer
    lookup_field = 'approval_token'
    lookup_url_kwarg = 'token'

    def update(self, request, *args, **kwargs):
        chat = self.get_object()
        if chat.status == ChatRequest.STATUS_CANCELLED:
            return Response({'detail': 'Chat was already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        chat.status = ChatRequest.STATUS_APPROVED
        chat.save()
        return Response({'detail': 'Chat approved successfully.'})

class ChatRequestCancelView(generics.UpdateAPIView):
    queryset = ChatRequest.objects.all()
    serializer_class = ChatRequestSerializer
    permission_classes = []
    lookup_field = 'approval_token'
    lookup_url_kwarg = 'token'

    def update(self, request, *args, **kwargs):
        chat = self.get_object()
        reason = request.data.get("reason", "")
        print(reason)
        chat.status = ChatRequest.STATUS_CANCELLED
        chat.cancelled_at=timezone.now()
        chat.cancellation_reason = reason
        chat.save()
        return Response({'detail': 'Chat cancelled successfully.'})



class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class=PageNumberPagination
    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(ChatRequest, id=chat_id)

        user = self.request.user
        role = getattr(user, 'role', None).upper()
        print(role)

        if role == 'TEACHER':
            teacher = get_object_or_404(Teacher, user=user)
            if chat.teacher != teacher:
               raise PermissionDenied("Acesss denied")
        elif role == 'STUDENT':
            student = get_object_or_404(Student, user=user)
            if chat.student != student:
                raise PermissionDenied("Access denied")
        elif role != 'ADMIN':
            raise PermissionDenied("Acesss denied")
        return ChatMessage.objects.filter(chat_request=chat).order_by('-timestamp')

class ChatRequestCreateView(generics.CreateAPIView):
    serializer_class = ChatRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        
            chat_request = serializer.save()
            
            frontend_base = settings.FRONTEND_URL  
            approve_url = f"{frontend_base}/chat/approve/{chat_request.approval_token}"
            cancel_url = f"{frontend_base}/chat/cancel/{chat_request.approval_token}"


            subject = "New Chat Request Pending Approval"
            message = (
                f"Teacher {chat_request.teacher} has requested to chat with student {chat_request.student}.\n\n"
                f"Approve: {approve_url}\n"
                f"Cancel: {cancel_url}"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
        


class ChatStatusCheckView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        user = request.user

       
        teacher = Teacher.objects.filter(user=user).first()
        if teacher:
           
            chat_request = ChatRequest.objects.filter(teacher=teacher, student_id=student_id).first()
            if chat_request:
                return Response({'id': chat_request.id, 'status': chat_request.status})
            else:
                return Response({'id': None, 'status': None}, status=200)

        
        student = Student.objects.filter(user=user).first()
        if student:
            
            if student.id != student_id:
                return Response({'detail': 'Forbidden: student can only check their own chat status.'}, status=403)

            
            assigned_teacher = student.assigned_teacher
            if not assigned_teacher:
                return Response({'detail': 'No assigned teacher for this student.'}, status=404)

            
            chat_request = ChatRequest.objects.filter(teacher=assigned_teacher, student=student).first()
            if chat_request:
                return Response({'id': chat_request.id, 'status': chat_request.status})
            else:
                return Response({'id': None, 'status': None}, status=200)

        
        return Response({'detail': 'User is neither a teacher nor a student.'}, status=403)


class ChatStatusByIdView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatStatusSerializer

    def get(self, request, chat_id):
        try:
            chat_request = ChatRequest.objects.get(id=chat_id)
            serializer = self.get_serializer(chat_request)
            return Response(serializer.data)
        except ChatRequest.DoesNotExist:
            return Response({'error': 'Chat request not found'}, status=404)

class CancelChatRequestsByTeacherView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]  

    def put(self, request, teacher_id):
        reason = request.data.get("reason", "")
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({'detail': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        chats_to_cancel = ChatRequest.objects.filter(teacher=teacher)
        updated_count = chats_to_cancel.update(status=ChatRequest.STATUS_CANCELLED,cancelled_at=timezone.now(),cancellation_reason=reason)

        return Response({
            'detail': f'Successfully cancelled {updated_count} chat request(s) for teacher {teacher_id}.'
        }, status=status.HTTP_200_OK)

class ChatRequestDetailView(generics.RetrieveAPIView):
    
    serializer_class = ChatRequestSerializer
    lookup_field = 'approval_token' 
    lookup_url_kwarg = 'token'
    permission_classes = []    
    def get_queryset(self):
        return ChatRequest.objects.select_related('teacher', 'student').all()

class CancelChatRequestForStudentView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]
    
    def put(self, request, teacher_id, student_id):
        reason = request.data.get("reason", "")
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            student = Student.objects.get(id=student_id, assigned_teacher=teacher)
        except (Teacher.DoesNotExist, Student.DoesNotExist):
            return Response({'detail': 'Teacher or Student not found'}, status=status.HTTP_404_NOT_FOUND)

        chats_to_cancel = ChatRequest.objects.filter(teacher=teacher, student=student)

        
        if not chats_to_cancel.exists():
            raise ValidationError({"detail": "No chat exists between this teacher and student."})

        updated_count = chats_to_cancel.update(status=ChatRequest.STATUS_CANCELLED,cancelled_at=timezone.now(),cancellation_reason=reason)

        return Response({
            'detail': f'Successfully cancelled {updated_count} chat request(s) for student {student_id} under teacher {teacher_id}.'
        }, status=status.HTTP_200_OK)