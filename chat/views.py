# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Max, F, ExpressionWrapper, BooleanField
from django.utils.html import escape
from django.contrib.auth import get_user_model
import logging

from .models import ChatRoom, Message
from products.models import Product

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required
def chat_list(request):
    # 자신이 참여한 채팅방 목록 가져오기
    chat_rooms = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    ).annotate(
        # 안 읽은 메시지 수 계산
        unread_count=Count(
            'messages', 
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        ),
        # 마지막 메시지 시간
        last_message_time=Max('messages__created_at')
    ).order_by('-updated_at')
    
    # 채팅방마다 상대방 정보 추가
    for room in chat_rooms:
        room.other_participant = room.participants.exclude(id=request.user.id).first()
        room.last_message_obj = room.messages.order_by('-created_at').first()
    
    return render(request, 'chat/chat_list.html', {
        'chat_rooms': chat_rooms
    })

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # 권한 확인
    if request.user not in chat_room.participants.all():
        messages.error(request, '이 채팅방에 접근할 권한이 없습니다.')
        return redirect('chat:chat_list')
    
    # 상대방 정보
    other_participant = chat_room.participants.exclude(id=request.user.id).first()
    
    # 메시지 불러오기
    messages_list = chat_room.messages.all()
    
    # 읽지 않은 메시지 읽음 처리
    unread_messages = messages_list.filter(
        sender=other_participant,
        is_read=False
    )
    
    for message in unread_messages:
        message.is_read = True
        message.save()
    
    # 관련 상품 정보
    product = chat_room.product
    
    return render(request, 'chat/chat_room.html', {
        'chat_room': chat_room,
        'messages': messages_list,
        'other_participant': other_participant,
        'product': product
    })

@login_required
def start_chat(request, user_id=None, product_id=None):
    # 채팅 시작 대상
    other_user = None
    product = None
    
    if user_id:
        other_user = get_object_or_404(User, id=user_id)
        
        # 자기 자신과는 채팅 불가
        if other_user == request.user:
            messages.error(request, '자기 자신과는 채팅할 수 없습니다.')
            return redirect('products:product_list')
        
        # 휴면 계정과는 채팅 불가
        if other_user.is_dormant:
            messages.error(request, '이 사용자는 휴면 상태입니다.')
            return redirect('products:product_list')
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        
        # 자신의 상품에 대해서는 채팅 불가
        if product.seller == request.user:
            messages.error(request, '자신의 상품에 대해서는 채팅을 시작할 수 없습니다.')
            return redirect('products:product_detail', product_id=product_id)
        
        # 차단된 상품은 채팅 불가
        if product.status == 'blocked':
            messages.error(request, '차단된 상품에 대해서는 채팅을 시작할 수 없습니다.')
            return redirect('products:product_list')
        
        # 판매자를 other_user로 설정
        other_user = product.seller
    
    if not other_user:
        messages.error(request, '채팅 대상을 찾을 수 없습니다.')
        return redirect('products:product_list')
    
    # 이미 존재하는 채팅방 확인
    existing_chat = ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    )
    
    if product:
        existing_chat = existing_chat.filter(product=product)
    
    if existing_chat.exists():
        # 이미 존재하는 채팅방으로 이동
        return redirect('chat:chat_room', room_id=existing_chat.first().id)
    
    # 새 채팅방 생성
    chat_room = ChatRoom.objects.create()
    chat_room.participants.add(request.user, other_user)
    
    if product:
        chat_room.product = product
        chat_room.save()
    
    logger.info(f"New chat room created: {request.user.username} with {other_user.username}")
    
    # 시스템 메시지 추가
    system_message = "대화가 시작되었습니다."
    if product:
        system_message = f"'{product.title}' 상품에 대한 대화가 시작되었습니다."
    
    Message.objects.create(
        chat_room=chat_room,
        sender=request.user,
        content=system_message
    )
    
    return redirect('chat:chat_room', room_id=chat_room.id)