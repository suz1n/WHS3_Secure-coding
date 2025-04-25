# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import escape
from django.core.exceptions import ValidationError
import logging
import re

from .forms import SignUpForm, UserUpdateForm
from products.models import Product

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # XSS 방지를 위한 이스케이프 처리
            username = escape(form.cleaned_data.get('username'))
            email = escape(form.cleaned_data.get('email'))
            intro = escape(form.cleaned_data.get('intro', ''))
            
            # 비밀번호 강도 검증
            password = form.cleaned_data.get('password1')
            if len(password) < 8:
                form.add_error('password1', '비밀번호는 최소 8자 이상이어야 합니다.')
                return render(request, 'accounts/signup.html', {'form': form})
            
            if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                form.add_error('password1', '비밀번호는 영문자, 숫자, 특수문자를 각각 하나 이상 포함해야 합니다.')
                return render(request, 'accounts/signup.html', {'form': form})
            
            user = form.save(commit=False)
            user.intro = intro
            user.save()
            
            # 클라이언트 IP 기록 (보안 로그)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            logger.info(f"New user registered: {username} from IP: {ip}")
            
            # 로그인 처리
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, '회원가입이 완료되었습니다!')
                return redirect('core:home')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 입력값 검증
        if not username or not password:
            messages.error(request, '아이디와 비밀번호를 모두 입력해주세요.')
            return render(request, 'accounts/login.html')
        
        # XSS 방지
        username = escape(username)
        
        # CSRF 토큰 검증은 Django에서 자동으로 처리
        
        # 로그인 시도 횟수 제한 (보안)
        session_key = f'login_attempts_{username}'
        login_attempts = request.session.get(session_key, 0)
        
        if login_attempts >= 5:
            messages.error(request, '로그인 시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.')
            logger.warning(f"Login attempt limit exceeded for username: {username}")
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_dormant:
                messages.error(request, '이 계정은 신고로 인해 휴면 상태입니다. 관리자에게 문의하세요.')
                logger.warning(f"Dormant account login attempt: {username}")
                return render(request, 'accounts/login.html')
            
            login(request, user)
            
            # 로그인 시도 횟수 초기화
            if session_key in request.session:
                del request.session[session_key]
            
            # IP 주소 저장
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            user.last_login_ip = ip
            user.save()
            
            logger.info(f"User logged in: {username} from IP: {ip}")
            
            return redirect('core:home')
        else:
            # 로그인 실패 시 시도 횟수 증가
            request.session[session_key] = login_attempts + 1
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logger.info(f"User logged out: {request.user.username}")
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('core:home')

@login_required
def profile_view(request):
    user_products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'products': user_products
    })

@login_required
def profile_update_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # XSS 방지를 위한 이스케이프 처리
            username = escape(form.cleaned_data.get('username'))
            intro = escape(form.cleaned_data.get('intro', ''))
            
            user = form.save(commit=False)
            user.intro = intro
            user.save()
            
            logger.info(f"User profile updated: {username}")
            messages.success(request, '프로필이 업데이트되었습니다.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})