// DOMContentLoaded 이벤트가 발생했을 때 실행될 함수
document.addEventListener('DOMContentLoaded', function() {
    // CSRF 토큰 생성 및 저장
    const csrfToken = generateCSRFToken();
    localStorage.setItem('csrfToken', csrfToken);
    
    // 모달 관련 요소
    const modals = document.querySelectorAll('.modal');
    const loginBtn = document.getElementById('login-btn');
    const signupBtn = document.getElementById('signup-btn');
    const sellBtn = document.getElementById('sell-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const closeButtons = document.querySelectorAll('.close-modal');
    
    // 로그인 상태 확인
    checkLoginStatus();
    
    // 모달 열기/닫기 이벤트 리스너
    loginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('login-modal').style.display = 'flex';
    });
    
    signupBtn.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('signup-modal').style.display = 'flex';
    });
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    sellBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // 로그인 상태 확인 후 모달 열기
        if (isLoggedIn()) {
            document.getElementById('sell-modal').style.display = 'flex';
        } else {
            alert('로그인이 필요한 서비스입니다.');
            document.getElementById('login-modal').style.display = 'flex';
        }
    });
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });
    
    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // 로그인 폼 제출 이벤트 리스너
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        // 이메일 유효성 검사
        if (!isValidEmail(email)) {
            alert('유효한 이메일 주소를 입력해주세요.');
            return;
        }
        
        // 비밀번호 유효성 검사
        if (password.length < 8) {
            alert('비밀번호는 최소 8자 이상이어야 합니다.');
            return;
        }
        
        // 보안 강화: 입력값 이스케이프 처리
        const safeEmail = escapeHTML(email);
        
        // 여기서 로그인 API 호출 (실제로는 서버로 요청을 보냄)
        login(safeEmail, password, csrfToken);
    });
    
    // 회원가입 폼 제출 이벤트 리스너
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('signup-username').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const passwordConfirm = document.getElementById('signup-password-confirm').value;
        
        // 이름 유효성 검사
        if (!isValidUsername(username)) {
            alert('이름은 2-20자의 영문, 숫자, 한글만 사용 가능합니다.');
            return;
        }
        
        // 이메일 유효성 검사
        if (!isValidEmail(email)) {
            alert('유효한 이메일 주소를 입력해주세요.');
            return;
        }
        
        // 비밀번호 유효성 검사
        if (!isStrongPassword(password)) {
            alert('비밀번호는 최소 8자, 영문자, 숫자, 특수문자를 포함해야 합니다.');
            return;
        }
        
        // 비밀번호 확인 일치 여부
        if (password !== passwordConfirm) {
            alert('비밀번호가 일치하지 않습니다.');
            return;
        }
        
        // 보안 강화: 입력값 이스케이프 처리
        const safeUsername = escapeHTML(username);
        const safeEmail = escapeHTML(email);
        
        // 여기서 회원가입 API 호출 (실제로는 서버로 요청을 보냄)
        signup(safeUsername, safeEmail, password, csrfToken);
    });
    
    // 상품 등록 폼 제출 이벤트 리스너
    const sellForm = document.getElementById('sell-form');
    sellForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const title = document.getElementById('product-title').value;
        const price = document.getElementById('product-price').value;
        const description = document.getElementById('product-description').value;
        const imageFile = document.getElementById('product-image').files[0];
        
        // 입력값 유효성 검사
        if (title.trim() === '') {
            alert('상품명을 입력해주세요.');
            return;
        }
        
        if (isNaN(price) || price <= 0) {
            alert('유효한 가격을 입력해주세요.');
            return;
        }
        
        if (description.trim() === '') {
            alert('상품 설명을 입력해주세요.');
            return;
        }
        
        if (!imageFile) {
            alert('상품 이미지를 선택해주세요.');
            return;
        }
        
        // 이미지 파일 유효성 검사
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validImageTypes.includes(imageFile.type)) {
            alert('JPG, PNG, GIF 형식의 이미지만 업로드 가능합니다.');
            return;
        }
        
        if (imageFile.size > 5 * 1024 * 1024) {
            alert('이미지 크기는 5MB 이하여야 합니다.');
            return;
        }
        
        // 보안 강화: 입력값 이스케이프 처리
        const safeTitle = escapeHTML(title);
        const safeDescription = escapeHTML(description);
        
        // 여기서 상품 등록 API 호출 (실제로는 서버로 요청을 보냄)
        registerProduct(safeTitle, price, safeDescription, imageFile, csrfToken);
    });
    
    // 상품 로드 및 표시
    loadProducts();
    
    // 검색 기능
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(function() {
        const searchTerm = escapeHTML(searchInput.value.trim());
        if (searchTerm.length >= 2) {
            searchProducts(searchTerm);
        } else if (searchTerm.length === 0) {
            loadProducts(); // 검색어가 없으면 모든 상품 표시
        }
    }, 300));
    
    // ============= 유틸리티 함수 =============
    
    // CSRF 토큰 생성 함수
    function generateCSRFToken() {
        try {
            // 충분한 엔트로피를 가진 토큰 생성
            const array = new Uint8Array(16);
            window.crypto.getRandomValues(array);
            
            // 16진수 문자열로 변환
            const token = Array.from(array)
                .map(b => b.toString(16).padStart(2, '0'))
                .join('');
            
            return token;
        } catch (error) {
            console.error('CSRF 토큰 생성 오류:', error);
            
            // 대체 방법 (fallback)
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let token = '';
            for (let i = 0; i < 32; i++) {
                token += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            return token;
        }
    }
    
    // HTML 이스케이프 처리 함수
    function escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    // XSS 필터링 함수 - 위험한 문자열 패턴 감지
    function detectXSS(input) {
        if (!input) return false;
        
        // 위험한 패턴 목록
        const dangerousPatterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /javascript\s*:/gi,
            /on\w+\s*=/gi,
            /data\s*:/gi,
            /<iframe/gi,
            /<embed/gi,
            /<object/gi,
            /<svg/gi,
            /document\./gi,
            /window\./gi,
            /eval\(/gi,
            /setTimeout\(/gi,
            /setInterval\(/gi,
            /new\s+Function\(/gi
        ];
        
        // 각 패턴 검사
        return dangerousPatterns.some(pattern => pattern.test(input));
    }
    
    // 입력값 유효성 검사 함수
    function validateInput(input, type) {
        if (!input) return false;
        
        // XSS 공격 시도 감지
        if (detectXSS(input)) {
            logActivity('security_alert', {
                type: 'xss_attempt',
                input: input.substring(0, 100), // 로그에는 일부만 기록
                timestamp: new Date().toISOString()
            });
            return false;
        }
        
        switch (type) {
            case 'email':
                return isValidEmail(input);
            case 'username':
                return isValidUsername(input);
            case 'password':
                return isStrongPassword(input);
            case 'text':
                return input.trim().length > 0 && input.trim().length <= 1000;
            case 'price':
                return !isNaN(input) && Number(input) >= 0 && Number(input) <= 100000000;
            default:
                return true;
        }
    }
    
    // 이메일 유효성 검사 함수
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // 사용자명 유효성 검사 함수
    function isValidUsername(username) {
        // 2-20자의 영문, 숫자, 한글만 사용 가능
        return /^[A-Za-z0-9가-힣]{2,20}$/.test(username);
    }
    
    // 비밀번호 강도 검사
    function isStrongPassword(password) {
        // 최소 8자, 영문자, 숫자, 특수문자 포함
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
        return passwordRegex.test(password);
    }
    
    // 로그인 상태 확인 함수
    function isLoggedIn() {
        // 토큰 검증
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        
        if (!token || !user) {
            return false;
        }
        
        try {
            // 토큰 만료 확인 (실제로는 서버에서 검증)
            const tokenParts = token.split('.');
            if (tokenParts.length !== 3) {
                return false;
            }
            
            const payload = JSON.parse(atob(tokenParts[1]));
            const exp = payload.exp;
            
            if (exp && Date.now() >= exp * 1000) {
                // 토큰 만료
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('토큰 검증 오류:', error);
            return false;
        }
    }
    
    // 관리자 권한 확인
    function isAdmin() {
        if (!isLoggedIn()) return false;
        
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        return userData.role === 'admin';
    }
    
    // 로그인 상태에 따라 UI 업데이트
    function checkLoginStatus() {
        const loginStatus = isLoggedIn();
        const loginBtn = document.getElementById('login-btn');
        const signupBtn = document.getElementById('signup-btn');
        const sellBtn = document.getElementById('sell-btn');
        const messagesBtn = document.getElementById('messages-btn');
        const mypageBtn = document.getElementById('mypage-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (loginStatus) {
            // 로그인 상태
            loginBtn.style.display = 'none';
            signupBtn.style.display = 'none';
            sellBtn.style.display = 'block';
            messagesBtn.style.display = 'block';
            mypageBtn.style.display = 'block';
            logoutBtn.style.display = 'block';
            
            // 사용자 정보 표시
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            if (userData.username) {
                const usernameSpan = document.getElementById('username-display') || document.createElement('span');
                usernameSpan.id = 'username-display';
                usernameSpan.textContent = `${escapeHTML(userData.username)}님`;
                usernameSpan.className = 'username-display';
                
                // 아직 추가되지 않았다면 추가
                if (!document.getElementById('username-display')) {
                    if (mypageBtn.parentNode) {
                        mypageBtn.parentNode.insertBefore(usernameSpan, mypageBtn);
                    }
                }
            }
        } else {
            // 로그아웃 상태
            loginBtn.style.display = 'block';
            signupBtn.style.display = 'block';
            sellBtn.style.display = 'none';
            messagesBtn.style.display = 'none';
            mypageBtn.style.display = 'none';
            logoutBtn.style.display = 'none';
            
            // 사용자 정보 제거
            const usernameSpan = document.getElementById('username-display');
            if (usernameSpan) {
                usernameSpan.remove();
            }
        }
    }
    
    // 디바운스 함수 (검색 입력 최적화)
    function debounce(func, delay) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    }
    
    // ============= API 함수 =============
    
    // 로그인 API 함수
    async function login(email, password, csrfToken) {
        try {
            // 실제로는 서버로 요청을 보내야 함
            // 현재는 간단한 시뮬레이션
            console.log('로그인 요청:', email);
            
            // 비밀번호 해시 (실제로는 서버에서 처리)
            const hashedPassword = await hashPassword(password);
            
            // 로그인 성공 시뮬레이션
            setTimeout(() => {
                // 예시 사용자 데이터 (실제로는 서버에서 받음)
                const userData = {
                    id: 1,
                    username: '사용자',
                    email: email,
                    role: 'user',
                    lastLogin: new Date().toISOString()
                };
                
                // JWT 토큰 생성 시뮬레이션
                const token = generateJWTToken(userData);
                
                // localStorage에 사용자 정보 저장 (실제로는 HttpOnly 쿠키에 JWT 토큰 저장)
                localStorage.setItem('user', JSON.stringify(userData));
                localStorage.setItem('token', token);
                
                // 세션 타임아웃 설정 (30분)
                setSessionTimeout(30);
                
                // CSRF 토큰 갱신
                const newCsrfToken = generateCSRFToken();
                localStorage.setItem('csrfToken', newCsrfToken);
                
                // UI 업데이트
                checkLoginStatus();
                
                // 모달 닫기
                document.getElementById('login-modal').style.display = 'none';
                
                // 로그인 성공 메시지
                showNotification('로그인되었습니다.', 'success');
                
                // 로그인 시도 기록 (감사 로그)
                logActivity('login_success', {
                    userId: userData.id,
                    email: email,
                    timestamp: new Date().toISOString(),
                    ip: '127.0.0.1' // 실제로는 서버에서 클라이언트 IP 기록
                });
            }, 500);
        } catch (error) {
            console.error('로그인 오류:', error);
            
            // 로그인 실패 메시지 (자세한 오류 정보 노출하지 않음)
            showNotification('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.', 'error');
            
            // 로그인 실패 기록 (감사 로그)
            logActivity('login_failed', {
                email: email,
                timestamp: new Date().toISOString(),
                ip: '127.0.0.1' // 실제로는 서버에서 클라이언트 IP 기록
            });
        }
    }
    
    // 비밀번호 해시 함수 (실제로는 서버에서 bcrypt 등으로 처리)
    async function hashPassword(password) {
        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(password);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            return hashHex;
        } catch (error) {
            console.error('비밀번호 해시 오류:', error);
            throw new Error('보안 오류가 발생했습니다.');
        }
    }
    
    // JWT 토큰 생성 (실제로는 서버에서 처리)
    function generateJWTToken(userData) {
        // 간단한 JWT 구조 시뮬레이션
        const header = {
            alg: 'HS256',
            typ: 'JWT'
        };
        
        const payload = {
            sub: userData.id,
            name: userData.username,
            email: userData.email,
            role: userData.role,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (30 * 60) // 30분 유효
        };
        
        // 실제로는 서명이 필요하지만 여기서는 생략
        const tokenParts = [
            btoa(JSON.stringify(header)),
            btoa(JSON.stringify(payload)),
            'signature_placeholder'
        ];
        
        return tokenParts.join('.');
    }
    
    // 세션 타임아웃 설정
    function setSessionTimeout(minutes) {
        // 기존 타이머 제거
        if (window.sessionTimeoutId) {
            clearTimeout(window.sessionTimeoutId);
        }
        
        // 새 타이머 설정
        window.sessionTimeoutId = setTimeout(() => {
            // 세션 만료 시 로그아웃
            if (isLoggedIn()) {
                logout();
                showNotification('세션이 만료되었습니다. 다시 로그인해주세요.', 'warning');
            }
        }, minutes * 60 * 1000);
        
        // 사용자 활동 모니터링
        document.addEventListener('click', resetSessionTimer);
        document.addEventListener('keypress', resetSessionTimer);
    }
    
    // 사용자 활동 시 세션 타이머 리셋
    function resetSessionTimer() {
        if (isLoggedIn()) {
            setSessionTimeout(30); // 30분으로 타이머 리셋
        }
    }
    
    // 사용자 활동 로깅
    function logActivity(action, data) {
        // 실제로는 서버에 로그 전송
        // 여기서는 콘솔에만 출력
        console.log(`활동 로그: ${action}`, data);
        
        // 로컬 스토리지에 최근 활동 저장
        const logs = JSON.parse(localStorage.getItem('activityLogs') || '[]');
        logs.push({
            action,
            ...data
        });
        
        // 로그 크기 제한 (최대 100개)
        while (logs.length > 100) {
            logs.shift();
        }
        
        localStorage.setItem('activityLogs', JSON.stringify(logs));
    }
    
    // 알림 표시 함수
    function showNotification(message, type = 'info') {
        // 기존 알림 제거
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // 새 알림 생성
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 알림 스타일
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '4px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            zIndex: '9999',
            transition: 'all 0.3s ease',
            maxWidth: '300px'
        });
        
        // 알림 타입에 따른 색상
        const colors = {
            info: {bg: '#4a6eb5', text: 'white'},
            success: {bg: '#28a745', text: 'white'},
            warning: {bg: '#ffc107', text: '#212529'},
            error: {bg: '#dc3545', text: 'white'}
        };
        
        if (colors[type]) {
            notification.style.backgroundColor = colors[type].bg;
            notification.style.color = colors[type].text;
        }
        
        // 알림 추가
        document.body.appendChild(notification);
        
        // 3초 후 알림 제거
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
        
        return notification;
    }
    
    // 로그아웃 함수
    function logout() {
        // 로그아웃 활동 기록
        if (isLoggedIn()) {
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            logActivity('logout', {
                userId: userData.id,
                email: userData.email,
                timestamp: new Date().toISOString()
            });
        }
        
        // 사용자 데이터 및 토큰 제거
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        
        // 이벤트 리스너 제거
        document.removeEventListener('click', resetSessionTimer);
        document.removeEventListener('keypress', resetSessionTimer);
        
        if (window.sessionTimeoutId) {
            clearTimeout(window.sessionTimeoutId);
            window.sessionTimeoutId = null;
        }
        
        // UI 업데이트
        checkLoginStatus();
        
        // 홈으로 리디렉션
        window.location.hash = '';
    }
    
    // 회원가입 API 함수
    async function signup(username, email, password, csrfToken) {
        try {
            // 입력값 검증
            if (!username || username.trim().length < 2 || username.trim().length > 20) {
                throw new Error('이름은 2-20자 사이여야 합니다.');
            }
            
            if (!email || !isValidEmail(email)) {
                throw new Error('유효한 이메일 주소를 입력해주세요.');
            }
            
            if (!password || !isStrongPassword(password)) {
                throw new Error('비밀번호는 최소 8자, 영문자, 숫자, 특수문자를 포함해야 합니다.');
            }
            
            // 비밀번호 해시 (실제로는 서버에서 처리)
            const hashedPassword = await hashPassword(password);
            
            // 회원가입 성공 시뮬레이션
            setTimeout(() => {
                // 새 사용자 생성
                const userData = {
                    id: Math.floor(Math.random() * 10000) + 1, // 임의의 ID 생성
                    username: username,
                    email: email,
                    role: 'user',
                    createdAt: new Date().toISOString()
                };
                
                // 사용자 저장 (실제로는 데이터베이스에 저장)
                const users = JSON.parse(localStorage.getItem('users') || '[]');
                
                // 이메일 중복 확인
                const existingUser = users.find(user => user.email === email);
                if (existingUser) {
                    showNotification('이미 등록된 이메일입니다.', 'error');
                    return;
                }
                
                users.push({
                    ...userData,
                    password: hashedPassword // 해시된 비밀번호 저장
                });
                
                localStorage.setItem('users', JSON.stringify(users));
                
                // 자동 로그인
                localStorage.setItem('user', JSON.stringify(userData));
                
                // JWT 토큰 생성 및 저장
                const token = generateJWTToken(userData);
                localStorage.setItem('token', token);
                
                // 세션 타임아웃 설정
                setSessionTimeout(30); // 30분
                
                // CSRF 토큰 갱신
                const newCsrfToken = generateCSRFToken();
                localStorage.setItem('csrfToken', newCsrfToken);
                
                // UI 업데이트
                checkLoginStatus();
                
                // 모달 닫기
                document.getElementById('signup-modal').style.display = 'none';
                
                // 성공 메시지
                showNotification('회원가입이 완료되었습니다.', 'success');
                
                // 회원가입 로그
                logActivity('signup_success', {
                    userId: userData.id,
                    email: email,
                    timestamp: new Date().toISOString()
                });
            }, 500);
        } catch (error) {
            console.error('회원가입 오류:', error);
            showNotification(error.message || '회원가입 중 오류가 발생했습니다.', 'error');
            
            // 회원가입 실패 로그
            logActivity('signup_failed', {
                email: email,
                error: error.message,
                timestamp: new Date().toISOString()
            });
        }
    }
    
    // 상품 등록 API 함수
    function registerProduct(title, price, description, imageFile, csrfToken) {
        // CSRF 토큰 검증
        const storedToken = localStorage.getItem('csrfToken');
        if (csrfToken !== storedToken) {
            showNotification('보안 오류: 토큰이 유효하지 않습니다.', 'error');
            return;
        }
        
        // 로그인 상태 확인
        if (!isLoggedIn()) {
            showNotification('로그인이 필요한 서비스입니다.', 'error');
            document.getElementById('login-modal').style.display = 'flex';
            return;
        }
        
        try {
            // 입력값 검증
            if (!title || title.trim().length < 2 || title.trim().length > 50) {
                throw new Error('상품명은 2-50자 사이여야 합니다.');
            }
            
            if (isNaN(price) || price <= 0 || price > 100000000) {
                throw new Error('유효한 가격을 입력해주세요 (1원-1억원).');
            }
            
            if (!description || description.trim().length < 10 || description.trim().length > 1000) {
                throw new Error('상품 설명은 10-1000자 사이여야 합니다.');
            }
            
            // 이미지 파일 검증
            if (!validateImageFile(imageFile)) {
                throw new Error('유효하지 않은 이미지 파일입니다.');
            }
            
            // 실제로는 서버로 요청을 보내야 함
            // 현재는 간단한 시뮬레이션
            console.log('상품 등록 요청:', title, price);
            
            // 현재 로그인한 사용자 정보 가져오기
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            
            // 이미지 URL 생성 (실제로는 서버에 업로드하고 URL을 받아야 함)
            // 여기서는 placeholder 이미지 사용
            let imageUrl = '/api/placeholder/400/300';
            
            // 이미지 파일을 Base64로 인코딩하여 저장 (실제로는 서버에 업로드)
            const reader = new FileReader();
            reader.onload = function(e) {
                // Base64 이미지 데이터 (실제 서비스에서는 매우 비효율적이므로 지양)
                const base64Image = e.target.result;
                
                // 상품 객체 생성
                const newProduct = {
                    id: Date.now(), // 유니크 ID 생성
                    title: escapeHTML(title.trim()),
                    price: Number(price),
                    description: escapeHTML(description.trim()),
                    image: imageUrl,
                    imageData: base64Image,
                    sellerId: userData.id,
                    sellerName: userData.username,
                    status: '판매중',
                    createdAt: new Date().toISOString(),
                    views: 0
                };
                
                // LocalStorage에서 기존 상품 목록 불러오기
                const products = JSON.parse(localStorage.getItem('products') || '[]');
                
                // 새 상품 추가
                products.push(newProduct);
                
                // 업데이트된 상품 목록 저장
                localStorage.setItem('products', JSON.stringify(products));
                
                // 모달 닫기
                document.getElementById('sell-modal').style.display = 'none';
                
                // 상품 목록 갱신
                loadProducts();
                
                // 알림
                showNotification('상품이 등록되었습니다.', 'success');
                
                // 상품 등록 로그
                logActivity('product_registered', {
                    userId: userData.id,
                    productId: newProduct.id,
                    productTitle: title,
                    timestamp: new Date().toISOString()
                });
                
                // 폼 초기화
                document.getElementById('sell-form').reset();
            };
            
            reader.readAsDataURL(imageFile);
        } catch (error) {
            console.error('상품 등록 오류:', error);
            showNotification(error.message || '상품 등록 중 오류가 발생했습니다.', 'error');
        }
    }
    
    // 이미지 파일 검증
    function validateImageFile(file) {
        if (!file) return false;
        
        // 파일 타입 검사
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validImageTypes.includes(file.type)) {
            showNotification('JPG, PNG, GIF 형식의 이미지만 업로드 가능합니다.', 'error');
            return false;
        }
        
        // 파일 크기 제한 (5MB)
        if (file.size > 5 * 1024 * 1024) {
            showNotification('이미지 크기는 5MB 이하여야 합니다.', 'error');
            return false;
        }
        
        return true;
    }
    
    // 상품 불러오기 및 보안 처리
    function loadProducts() {
        try {
            // 실제로는 서버로 요청을 보내야 함
            // 현재는 LocalStorage에서 데이터 로드
            const products = JSON.parse(localStorage.getItem('products') || '[]');
            
            // 최신순으로 정렬
            products.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            
            // 숨겨진(삭제된) 상품 필터링
            const visibleProducts = products.filter(product => product.status !== '삭제됨');
            
            // 현재 로그인한 사용자 (관리자가 아니라면 차단된 판매자의 상품 숨김)
            const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
            const isAdmin = currentUser.role === 'admin';
            
            // 차단된 사용자 목록 불러오기
            const blockedUsers = JSON.parse(localStorage.getItem('blockedUsers') || '[]');
            
            // 관리자가 아니라면 차단된 판매자의 상품 필터링
            const filteredProducts = isAdmin 
                ? visibleProducts 
                : visibleProducts.filter(product => !blockedUsers.includes(product.sellerId));
            
            displayProducts(filteredProducts);
        } catch (error) {
            console.error('상품 로드 오류:', error);
            showNotification('상품을 불러오는 중 오류가 발생했습니다.', 'error');
        }
    }
    
    // 상품 검색 API 함수
    function searchProducts(searchTerm) {
        try {
            // 검색어 검증 및 이스케이프
            if (!searchTerm || searchTerm.trim().length === 0) {
                loadProducts();
                return;
            }
            
            const sanitizedSearchTerm = escapeHTML(searchTerm.trim().toLowerCase());
            
            // 검색어 길이 제한
            if (sanitizedSearchTerm.length < 2) {
                showNotification('검색어는 최소 2자 이상 입력해주세요.', 'info');
                return;
            }
            
            // XSS 방지
            document.getElementById('search-input').value = sanitizedSearchTerm;
            
            // 실제로는 서버로 요청을 보내야 함
            // 현재는 LocalStorage에서 데이터 필터링
            const products = JSON.parse(localStorage.getItem('products') || '[]');
            
            // 숨겨진 상품 필터링
            const visibleProducts = products.filter(product => product.status !== '삭제됨');
            
            // 검색어로 필터링 (제목, 설명에서 검색)
            const filteredProducts = visibleProducts.filter(product => 
                product.title.toLowerCase().includes(sanitizedSearchTerm) ||
                product.description.toLowerCase().includes(sanitizedSearchTerm)
            );
            
            // 검색 로그 저장
            logActivity('product_search', {
                searchTerm: sanitizedSearchTerm,
                resultCount: filteredProducts.length,
                timestamp: new Date().toISOString()
            });
            
            // 결과 표시
            displayProducts(filteredProducts);
            
            // 검색 결과 메시지
            if (filteredProducts.length === 0) {
                showNotification(`'${sanitizedSearchTerm}'에 대한 검색 결과가 없습니다.`, 'info');
            } else {
                showNotification(`'${sanitizedSearchTerm}'에 대한 검색 결과: ${filteredProducts.length}개의 상품을 찾았습니다.`, 'success');
            }
        } catch (error) {
            console.error('검색 오류:', error);
            showNotification('검색 중 오류가 발생했습니다.', 'error');
        }
    }
    
    // 상품 표시 함수 (XSS 방지)
    function displayProducts(products) {
        const productGrid = document.getElementById('product-grid');
        
        // 기존 상품 제거
        productGrid.innerHTML = '';
        
        if (products.length === 0) {
            const noProductsMsg = document.createElement('p');
            noProductsMsg.className = 'no-products-message';
            noProductsMsg.textContent = '등록된 상품이 없습니다.';
            productGrid.appendChild(noProductsMsg);
            return;
        }
        
        // 상품 추가 (안전한 DOM 조작)
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.dataset.productId = product.id;
            
            // 보안 강화: innerHTML 대신 DOM 조작 사용
            const productImage = document.createElement('img');
            productImage.className = 'product-image';
            productImage.src = product.image || product.imageData || '/api/placeholder/250/200';
            productImage.alt = product.title ? escapeHTML(product.title) : '상품 이미지';
            productImage.onerror = function() {
                this.src = '/api/placeholder/250/200'; // 이미지 로드 실패 시 대체 이미지
            };
            
            const productInfo = document.createElement('div');
            productInfo.className = 'product-info';
            
            const productTitle = document.createElement('h3');
            productTitle.className = 'product-title';
            productTitle.textContent = product.title ? escapeHTML(product.title) : '상품명 없음';
            
            const productPrice = document.createElement('p');
            productPrice.className = 'product-price';
            
            // 가격 정보 보안 처리 및 포맷팅
            let formattedPrice = '가격 정보 없음';
            if (product.price && !isNaN(product.price)) {
                formattedPrice = `${Number(product.price).toLocaleString()}원`;
            }
            productPrice.textContent = formattedPrice;
            
            const productSeller = document.createElement('p');
            productSeller.className = 'product-seller';
            
            // 판매자 정보 보안 처리
            let sellerInfo = '판매자 정보 없음';
            if (product.sellerName || product.seller) {
                sellerInfo = `판매자: ${escapeHTML(product.sellerName || product.seller)}`;
            }
            productSeller.textContent = sellerInfo;
            
            // 판매 상태 표시
            if (product.status && product.status !== '판매중') {
                const statusBadge = document.createElement('span');
                statusBadge.className = `status-badge status-${product.status.toLowerCase().replace(/\s+/g, '-')}`;
                statusBadge.textContent = product.status;
                productInfo.appendChild(statusBadge);
            }
            
            productInfo.appendChild(productTitle);
            productInfo.appendChild(productPrice);
            productInfo.appendChild(productSeller);
            
            productCard.appendChild(productImage);
            productCard.appendChild(productInfo);
            
            productGrid.appendChild(productCard);
            
            // 상품 클릭 이벤트 (이벤트 위임 대신 각 상품에 개별 이벤트 부여)
            productCard.addEventListener('click', function(e) {
                // 클릭 이벤트 추적
                logActivity('product_view', {
                    productId: product.id,
                    productTitle: product.title,
                    timestamp: new Date().toISOString()
                });
                
                // 상품 상세 페이지로 이동 또는 모달 표시
                showProductDetails(product.id);
            });
        });
    }
    
    // 페이지 초기화 함수
    function initializePage() {
        // 초기 CSRF 토큰 생성
        const csrfToken = generateCSRFToken();
        localStorage.setItem('csrfToken', csrfToken);
        
        // 로그인 상태 확인
        checkLoginStatus();
        
        // 상품 목록 로드
        loadProducts();
        
        // 관리자 메뉴 표시 여부
        const adminMenuLink = document.getElementById('admin-menu');
        if (adminMenuLink) {
            adminMenuLink.style.display = isAdmin() ? 'block' : 'none';
        }
        
        // 보안 로그
        logActivity('page_load', {
            url: window.location.href,
            timestamp: new Date().toISOString()
        });
    }
    
    // 페이지 로드 시 초기화
    window.addEventListener('load', initializePage);
});