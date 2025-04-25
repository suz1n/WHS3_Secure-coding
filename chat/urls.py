# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:room_id>/', views.chat_room, name='chat_room'),
    path('start/user/<int:user_id>/', views.start_chat, name='start_chat_with_user'),
    path('start/product/<int:product_id>/', views.start_chat, name='start_chat_for_product'),
]

# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.html import escape
from django.db.models import Q
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
import logging

User = get_user_model()

# 로깅 설정
logger = logging.getLogger(__name__)

@login_required
def chat_list(request):
    # 사용자가 참여한 채팅방 가져오기
    chat_rooms = ChatRoom.objects.filter(participants=request.user, is_active=True)
    
    # 각 채팅방의 마지막 메시지와 상대방 정보 추가
    for room in chat_rooms:
        # 마지막 메시지
        room.last_message = Message.objects.filter(chat_room=room).order_by('-created_at').first()
        
        # 채팅방 상대방
        room.other_participant = room.participants.exclude(id=request.user.id).first()
        
        # 읽지 않은 메시지 수
        room.unread_count = Message.objects.filter(
            chat_room=room, 
            sender__id=room.other_participant.id, 
            is_read=False
        ).count()
    
    return render(request, 'chat/chat_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # 권한 확인
    if request.user not in chat_room.participants.all():
        logger.warning(f"Unauthorized chat room access attempt: {request.user.username} tried to access room {room_id}")
        return redirect('chat:chat_list')
    
    # 상대방 정보 가져오기
    other_participant = chat_room.participants.exclude(id=request.user.id).first()
    
    # 메시지 가져오기
    messages = Message.objects.filter(chat_room=chat_room).order_by('created_at')
    
    # 읽지 않은 메시지 읽음 처리
    unread_messages = messages.filter(sender=other_participant, is_read=False)
    for message in unread_messages:
        message.is_read = True
        message.save()
    
    # AJAX 요청 처리 (새 메시지 전송)
    if request.method == 'POST' and request.is_ajax():
        content = escape(request.POST.get('content', '').strip())
        
        if content:
            # 메시지 저장
            message = Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content
            )
            
            # 로깅
            logger.info(f"New message