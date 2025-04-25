# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.html import escape
from django.utils import timezone
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # 방 참여자인지 확인
        if not await self.is_room_participant():
            logger.warning(f"Unauthorized chat room access attempt: {self.scope['user']} tried to access room {self.room_id}")
            await self.close()
            return
        
        # 채널 레이어에 그룹 추가
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # XSS 방지
        message = escape(message)
        
        if not message.strip():
            return
        
        # 길이 제한
        if len(message) > 500:
            message = message[:497] + '...'
        
        # 메시지 저장
        message_obj = await self.save_message(message)
        
        # 그룹으로 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.scope['user'].id,
                'sender_username': self.scope['user'].username,
                'timestamp': message_obj.created_at.isoformat()
            }
        )
    
    async def chat_message(self, event):
        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def is_room_participant(self):
        try:
            # 인증된 사용자인지 확인
            if not self.scope['user'].is_authenticated:
                return False
            
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.scope['user'].id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        
        # 채팅방 마지막 활동 시간 업데이트
        room.updated_at = timezone.now()
        room.save()
        
        # 메시지 저장
        message = Message.objects.create(
            chat_room=room,
            sender=self.scope['user'],
            content=content
        )
        
        return message