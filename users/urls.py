# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password/change/', views.change_password, name='change_password'),
]

# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, ProfileUpdateForm, PasswordChangeForm
import re
from django.utils.html import escape
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def validate_password(password):
    """비밀번호 유효성 검사"""
    # 최소 8자, 영문자, 숫자, 특수문자 포함
    if len(password) < 8:
        return False
    if not re.search('[A-Za-z]', password):
        return False
    if not re.search('[0-9]', password):
        return False
    if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = escape(form.cleaned_data.get('username'))
            email = escape(form.cleaned_data.get('email'))
            password = form.cleaned_data.get('password')
            password_confirm = form.cleaned_data.get('password_confirm')
            
            # 추가 유효성 검사
            if not validate_password(password):
                messages.error(request, "비밀번호는 최소 8자, 영문자, 숫자, 특수문자를 포함해야 합니다.")
                return render(request, 'users/signup.html', {'form': form})
                
            if password != password_confirm:
                messages.error(request, "비밀번호가 일치하지 않습니다.")
                return render(request, 'users/signup.html', {'form': form})
            
            # 사용자 생성
            user = form.save(commit=False)
            user.set_password(password)  # 비밀번호 해싱
            user.save()
            
            # 로깅
            logger.info(f"New user registered: {username}")
            
            # 로그인
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('products:home')
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = escape(form.cleaned_data.get('email'))
            password = form.cleaned_data.get('password')
            
            # 이메일로 사용자 찾기
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    
                    # IP 주소 저장 (보안 로그용)
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    user.last_login_ip = ip
                    user.save()
                    
                    # 로깅
                    logger.info(f"User login: {user.username}")
                    
                    return redirect('products:home')
                else:
                    messages.error(request, "이메일 또는 비밀번호가 올바르지 않습니다.")
            except User.DoesNotExist:
                messages.error(request, "이메일 또는 비밀번호가 올바르지 않습니다.")
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    # 로깅
    logger.info(f"User logout: {request.user.username}")
    
    logout(request)
    return redirect('products:home')

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필이 업데이트되었습니다.")
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'users/update_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            new_password_confirm = form.cleaned_data.get('new_password_confirm')
            
            # 현재 비밀번호 확인
            if not request.user.check_password(current_password):
                messages.error(request, "현재 비밀번호가 올바르지 않습니다.")
                return render(request, 'users/change_password.html', {'form': form})
                
            # 새 비밀번호 유효성 검사
            if not validate_password(new_password):
                messages.error(request, "비밀번호는 최소 8자, 영문자, 숫자, 특수문자를 포함해야 합니다.")
                return render(request, 'users/change_password.html', {'form': form})
                
            # 새 비밀번호 일치 확인
            if new_password != new_password_confirm:
                messages.error(request, "새 비밀번호가 일치하지 않습니다.")
                return render(request, 'users/change_password.html', {'form': form})
            
            # 비밀번호 변경
            request.user.set_password(new_password)
            request.user.save()
            
            # 로깅
            logger.info(f"Password changed for user: {request.user.username}")
            
            # 세션 업데이트
            update_session_auth_hash(request, request.user)
            
            messages.success(request, "비밀번호가 변경되었습니다.")
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})