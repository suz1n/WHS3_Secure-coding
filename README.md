# Tiny_Second-hand_Shopping_Platform

Tiny Second-hand Shopping Platform – WhiteHat School 3rd Secure Coding

## 기능

- 회원가입/로그인/로그아웃
- 상품 등록/조회/수정/삭제
- 실시간 채팅
- 신고 기능
- 마이페이지
- 관리자 기능

## 설치 및 실행

### 요구사항

- Python 3.10 이상
- Node.js 16 이상
- Redis

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/secondhand_platform.git
cd secondhand_platform

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 정적 파일 수집
python manage.py collectstatic
```

### 실행

```bash
# 개발 서버 실행
python manage.py runserver

# 채팅 기능을 위한 Daphne 서버 실행 (선택사항)
daphne -p 8001 secondhand_platform.asgi:application
```

## 보안 기능

- CSRF 보호
- XSS 방지
- SQL 인젝션 방지
- 비밀번호 강도 검증
- Rate Limiting
- 로그인 시도 제한
- 파일 업로드 보안
- 세션 보안

## 프로젝트 구조

```
secondhand_platform/
├── manage.py
├── requirements.txt
├── README.md
├── secondhand_platform/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   └── ...
├── products/
│   ├── models.py
│   ├── views.py
│   └── ...
├── chat/
│   ├── models.py
│   ├── consumers.py
│   └── ...
├── reports/
│   ├── models.py
│   ├── views.py
│   └── ...
└── static/
    ├── css/
    ├── js/
    └── ...
```

## 기여 방법

1. 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다.
