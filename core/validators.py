# core/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.html import escape

def validate_username(value):
    """
    사용자명 유효성 검증
    - 영문, 숫자, 한글 조합 (2-20자)
    """
    if not re.match(r'^[A-Za-z0-9가-힣]{2,20}$', value):
        raise ValidationError('사용자명은 2-20자의 영문, 숫자, 한글만 사용 가능합니다.')
    return value

def validate_password(value):
    """
    비밀번호 유효성 검증
    - 최소 8자, 영문자, 숫자, 특수문자 포함
    """
    if len(value) < 8:
        raise ValidationError('비밀번호는 최소 8자 이상이어야 합니다.')
    
    if not re.search(r'[A-Za-z]', value):
        raise ValidationError('비밀번호는 최소 하나의 영문자를 포함해야 합니다.')
    
    if not re.search(r'\d', value):
        raise ValidationError('비밀번호는 최소 하나의 숫자를 포함해야 합니다.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('비밀번호는 최소 하나의 특수문자를 포함해야 합니다.')
    
    return value

def validate_image_size(file):
    """
    이미지 크기 검증
    - 최대 5MB
    """
    # 5MB = 5 * 1024 * 1024 bytes
    max_size = 5 * 1024 * 1024
    
    if file.size > max_size:
        raise ValidationError('이미지 크기는 5MB를 초과할 수 없습니다.')
    
    return file

def validate_image_extension(file):
    """
    이미지 확장자 검증
    - jpg, jpeg, png, gif만 허용
    """
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = file.name.split('.')[-1].lower()
    
    if ext not in valid_extensions:
        raise ValidationError('JPG, PNG, GIF 형식의 이미지만 업로드 가능합니다.')
    
    return file

def sanitize_text(text):
    """
    텍스트 이스케이프 처리
    """
    if not text:
        return ''
    
    return escape(text)