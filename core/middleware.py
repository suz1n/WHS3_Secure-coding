# core/middleware.py
import re
import time
import logging
from django.conf import settings
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    """
    보안 관련 기능을 처리하는 미들웨어
    - CSRF 토큰 검증 (Django 내장)
    - XSS 공격 패턴 탐지
    - SQL 인젝션 패턴 탐지
    - Rate Limiting 적용
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 요청 제한 설정 (IP별로 1분당 최대 60회)
        self.rate_limit = getattr(settings, 'RATE_LIMIT', 60)
        self.time_window = 60  # 1분
        self.ip_requests = {}
        
    def process_request(self, request):
        # IP 주소 가져오기
        ip = self.get_client_ip(request)
        
        # Rate Limiting
        if self.is_rate_limited(ip):
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return HttpResponseForbidden("요청 횟수가 제한을 초과했습니다. 잠시 후 다시 시도해주세요.")
        
        # XSS 및 SQL 인젝션 공격 패턴 탐지
        if request.method == 'POST':
            # 로그인, 회원가입 등 민감한 페이지 제외
            sensitive_urls = [reverse('accounts:login'), reverse('accounts:signup')]
            if request.path not in sensitive_urls:
                for key, value in request.POST.items():
                    if isinstance(value, str):
                        # XSS 패턴 검출
                        if self.detect_xss(value):
                            logger.warning(f"XSS attack attempt detected from IP: {ip}, path: {request.path}")
                            return HttpResponseForbidden("잠재적인 보안 위협이 감지되었습니다.")
                        
                        # SQL 인젝션 패턴 검출
                        if self.detect_sql_injection(value):
                            logger.warning(f"SQL injection attempt detected from IP: {ip}, path: {request.path}")
                            return HttpResponseForbidden("잠재적인 보안 위협이 감지되었습니다.")
        
        return None
    
    def process_response(self, request, response):
        # 보안 관련 HTTP 헤더 추가
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip):
        current_time = time.time()
        
        # 현재 IP의 요청 기록 가져오기
        ip_record = self.ip_requests.get(ip, {'count': 0, 'timestamps': []})
        
        # 시간 초과된 타임스탬프 제거
        ip_record['timestamps'] = [ts for ts in ip_record['timestamps'] if current_time - ts < self.time_window]
        
        # 현재 요청 추가
        ip_record['timestamps'].append(current_time)
        ip_record['count'] = len(ip_record['timestamps'])
        
        # 저장
        self.ip_requests[ip] = ip_record
        
        # 제한 초과 여부 확인
        return ip_record['count'] > self.rate_limit
    
    def detect_xss(self, value):
        # XSS 공격 패턴 탐지
        xss_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<img.*?onerror',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    def detect_sql_injection(self, value):
        # SQL 인젝션 공격 패턴 탐지
        sql_patterns = [
            r'\b(select|insert|update|delete|drop|union|exec|declare)\b.*?',
            r'--',
            r'/\*.*?\*/',
            r';\s*$',
            r'(AND|OR)\s+\d+\s*=\s*\d+',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False