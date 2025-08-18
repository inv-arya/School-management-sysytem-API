from rest_framework import serializers
from .models import ChatRequest, ChatMessage

class ChatRequestSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()  
    student_name = serializers.SerializerMethodField()
    class Meta:
        model = ChatRequest
        fields = [
            'id',
            'teacher',
            'teacher_name',
            'student',
            'student_name',
            'status',
            'created_at',
            'cancelled_at',          
            'cancellation_reason',
        ]
    def get_teacher_name(self, obj):
        print("dfds")
        teacher = obj.teacher
        print("Teacher:", teacher)
        if teacher:
            return f"{teacher.first_name} {teacher.last_name}".strip()
        return ""

    def get_student_name(self, obj):
        student = obj.student
        if student:
            return f"{student.first_name} {student.last_name}".strip()
        return ""
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_request', 'sender_type', 'message', 'timestamp']
class ChatRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = ['student']

    def validate(self, data):
        teacher = self.context['request'].user.teacher  
        student = data['student']
        print("Checking ChatRequest for:", teacher, student)
        if ChatRequest.objects.filter(teacher=teacher, student=student).exists():
            print("Chat request already exists")
            raise serializers.ValidationError("Chat request already exists.")
        return data

    def create(self, validated_data):
        teacher = self.context['request'].user.teacher
        chat_request = ChatRequest.objects.create(
            teacher=teacher,
            student=validated_data['student'],
            status=ChatRequest.STATUS_PENDING
        )
        return chat_request
    
class ChatStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    status = serializers.IntegerField(allow_null=True)
