from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRequest, ChatMessage
from teachers.models import Teacher
from students.models import Student
from rest_framework import serializers
from .serializers import ChatRequestCreateSerializer, ChatMessageSerializer,ChatRequestSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import PermissionDenied

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '') == 'ADMIN'

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
        chat.status = ChatRequest.STATUS_CANCELLED
        chat.save()
        return Response({'detail': 'Chat cancelled successfully.'})

class ChatMessageCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, 'role', None)
        chat = serializer.validated_data['chat_request']

        if chat.status != ChatRequest.STATUS_APPROVED:
            raise serializers.ValidationError("Chat is not approved yet.")

        if role == 'TEACHER':
            teacher = get_object_or_404(Teacher, user=user)
            if chat.teacher != teacher:
                raise permissions.PermissionDenied("Not your chat.")
            sender_type = ChatMessage.SENDER_TEACHER
        elif role == 'STUDENT':
            student = get_object_or_404(Student, user=user)
            if chat.student != student:
                raise permissions.PermissionDenied("Not your chat.")
            sender_type = ChatMessage.SENDER_STUDENT
        else:
            raise permissions.PermissionDenied("Invalid user role for messaging.")

        serializer.save(sender_type=sender_type)

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(ChatRequest, id=chat_id)

        user = self.request.user
        role = getattr(user, 'role', None)
        print(role)

        if role == 'teacher':
            teacher = get_object_or_404(Teacher, user=user)
            if chat.teacher != teacher:
               raise PermissionDenied("Acesss denied")
        elif role == 'student':
            student = get_object_or_404(Student, user=user)
            if chat.student != student:
                raise PermissionDenied("Access denied")
        elif role != 'admin':
            raise PermissionDenied("Acesss denied")
        return ChatMessage.objects.filter(chat_request=chat).order_by('timestamp')

class ChatRequestCreateView(generics.CreateAPIView):
    serializer_class = ChatRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        chat_request = serializer.save()
        
        # Build approve/cancel URLs for admin email
        approve_url = f"{settings.BACKEND_URL}/api/chat/requests/approve/{chat_request.approval_token}/"
        cancel_url = f"{settings.BACKEND_URL}/api/chat/requests/cancel/{chat_request.approval_token}/"

        subject = "New Chat Request Pending Approval"
        message = (
            f"Teacher {chat_request.teacher} has requested to chat with student {chat_request.student}.\n\n"
            f"Approve: {approve_url}\n"
            f"Cancel: {cancel_url}"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])