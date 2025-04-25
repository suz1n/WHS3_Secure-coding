# core/utils.py
import re
from django.utils.html import escape

def clean_input(input_str):
    """
    입력값 이스케이프 처리 및 공백 정리
    """
    if not input_str:
        return ""
    cleaned = escape(input_str).strip()
    # 연속된 공백 제거
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def detect_xss(input_str):
    """
    XSS 공격 패턴 탐지
    """
    if not input_str:
        return False
    
    dangerous_patterns = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
        r'javascript\s*:',
        r'on\w+\s*=',
        r'data\s*:',
        r'<iframe',
        r'<embed',
        r'<object',
        r'<svg',
        r'document\.',
        r'window\.',
        r'eval\(',
        r'setTimeout\(',
        r'setInterval\(',
        r'new\s+Function\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    
    return False

def validate_password_strength(password):
    """
    비밀번호 강도 검증
    """
    # 최소 8자 이상
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."
    
    # 영문자 포함
    if not re.search(r'[A-Za-z]', password):
        return False, "비밀번호는 최소 하나의 영문자를 포함해야 합니다."
    
    # 숫자 포함
    if not re.search(r'\d', password):
        return False, "비밀번호는 최소 하나의 숫자를 포함해야 합니다."
    
    # 특수문자 포함
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호는 최소 하나의 특수문자를 포함해야 합니다."
    
    # 일반적인 패턴 체크
    common_patterns = [
        r'password', r'12345', r'qwerty', r'admin', r'welcome',
        r'abcdef', r'123456', r'qwerty', r'abc123'
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            return False, "비밀번호가 너무 간단하거나, 흔한 패턴을 포함하고 있습니다."
    
    return True, "강력한 비밀번호입니다."