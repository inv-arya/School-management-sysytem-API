import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRequest, ChatMessage
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        user = self.scope['user']
        if not user.is_authenticated or not user.is_active:
            await self.close(code=4001)
            return
        
        if await self.has_access():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self):
                
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        print("111111111111")
        user=await self._refresh_user(user)
        print(user.is_active)
        if not user.is_active:
            print("222222222")
            await self.close(code=4001) 
        chat_message = await self.save_message(message, user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': await self.get_sender_display(user),
                'timestamp': chat_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def has_access(self):
        try:
            chat = ChatRequest.objects.get(id=self.chat_id)
            user = self.scope['user']
            if not user.is_authenticated:
                return False
            role = getattr(user, 'role', '').upper()
            if role == 'TEACHER':
                return chat.teacher.user == user
            elif role == 'STUDENT':
                return chat.student.user == user
            elif role == 'ADMIN':
                return True
            return False
        except ChatRequest.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message, user):
        chat = ChatRequest.objects.get(id=self.chat_id)
        if chat.status != ChatRequest.STATUS_APPROVED:
            raise PermissionDenied("Chat is not approved.")
        
        role = getattr(user, 'role', '').upper()
        if role == 'TEACHER':
            if chat.teacher.user != user:
                raise PermissionDenied("Not your chat.")
            sender_type = ChatMessage.SENDER_TEACHER
        elif role == 'STUDENT':
            if chat.student.user != user:
                raise PermissionDenied("Not your chat.")
            sender_type = ChatMessage.SENDER_STUDENT
        else:
            raise PermissionDenied("Invalid user role.")
        
        return ChatMessage.objects.create(
            chat_request=chat,
            sender_type=sender_type,
            message=message
        )

    @database_sync_to_async
    def get_sender_display(self, user):   
        role = getattr(user, 'role', '').upper()
        if role == 'TEACHER':           
            return f"Teacher: {user.teacher}"
        elif role == 'STUDENT':
            return f"Student: {user.student}"
        return "Unknown"
    
    @database_sync_to_async
    def _refresh_user(self, user):
        """Fetch latest user instance from DB to ensure up-to-date status."""
        
        User = get_user_model()
        return User.objects.get(id=user.id)