from rest_framework import serializers
from .models import ChatRequest, ChatMessage

class ChatRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class ChatRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRequest
        fields = ['student']

    def validate(self, data):
        teacher = self.context['request'].user.teacher  # assuming Teacher linked to user
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
