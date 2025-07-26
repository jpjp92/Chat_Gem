# config/logincss.py
"""
로그인 페이지를 위한 트렌디한 CSS 스타일
"""

TRENDY_LOGIN_CSS = """
<style>
/* 전체 배경 그라데이션 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    min-height: 100vh;
}

/* 메인 컨테이너 설정 */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 100%;
}

/* 로그인 카드 컨테이너 */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    padding: 2rem 1rem;
}

/* 글래스모피즘 로그인 카드 */
.login-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
    padding: 3rem 2.5rem;
    width: 100%;
    max-width: 420px;
    position: relative;
    overflow: hidden;
    animation: cardFloat 6s ease-in-out infinite;
}

/* 카드 플로팅 애니메이션 */
@keyframes cardFloat {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(0.5deg); }
}

/* 로그인 카드 배경 장식 */
.login-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    animation: rotate 10s linear infinite;
    z-index: -1;
}

@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 로고/제목 스타일 */
.login-title {
    text-align: center;
    margin-bottom: 2rem;
}

.login-title h1 {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff, #f0f0f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
}

.login-subtitle {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 2.5rem;
    font-weight: 400;
}


/* 입력 필드 스타일링 - 수정 부분 */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.15) !important;  /* 기존: 0.1 → 0.15로 더 밝게 */
    border: 2px solid rgba(255, 255, 255, 0.3) !important;  /* 기존: 0.2 → 0.3으로 더 선명하게 */
    border-radius: 16px !important;
    color: white !important;
    font-size: 1.1rem !important;
    padding: 1rem 1.25rem !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px);
}

.stTextInput > div > div > input:focus {
    border-color: rgba(255, 255, 255, 0.7) !important;  /* 기존: 0.6 → 0.7로 더 밝게 */
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3) !important;  /* 기존: 0.2 → 0.3으로 글로우 강화 */
    background: rgba(255, 255, 255, 0.2) !important;  /* 기존: 0.15 → 0.2로 포커스 시 더 밝게 */
    outline: none !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255, 255, 255, 0.7) !important;  /* 기존: 0.6 → 0.7로 플레이스홀더 더 선명하게 */
}

/* 레이블 스타일 */
.stTextInput label {
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    margin-bottom: 0.5rem !important;
}

/* 폼 버튼 스타일 */
.stFormSubmitButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: white !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4) !important;
}

.stFormSubmitButton > button:active {
    transform: translateY(0px) !important;
}

/* 버튼 반짝임 효과 */
.stFormSubmitButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s;
}

.stFormSubmitButton > button:hover::before {
    left: 100%;
}

/* 성공/에러 메시지 스타일 */
.stSuccess {
    background: rgba(76, 175, 80, 0.2) !important;
    border: 1px solid rgba(76, 175, 80, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

.stError {
    background: rgba(244, 67, 54, 0.2) !important;
    border: 1px solid rgba(244, 67, 54, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

/* 플로팅 파티클 효과 */
.particle {
    position: fixed;
    pointer-events: none;
    width: 6px;
    height: 6px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    animation: float 15s infinite linear;
    z-index: -1;
}

@keyframes float {
    0% {
        transform: translateY(100vh) rotate(0deg);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(-100vh) rotate(360deg);
        opacity: 0;
    }
}

/* 기능 소개 섹션 */
.feature-section {
    text-align: center;
    margin-top: 2rem;
    color: white;
}

.feature-grid {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
}

.feature-item {
    text-align: center;
    flex: 1;
    min-width: 120px;
    padding: 0.5rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.feature-item:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    display: block;
}

.feature-text {
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
    font-weight: 500;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .login-card {
        margin: 1rem;
        padding: 2rem 1.5rem;
    }
    
    .login-title h1 {
        font-size: 2rem;
    }
    
    .login-subtitle {
        font-size: 1rem;
    }
    
    .feature-grid {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .feature-item {
        min-width: auto;
    }
}

/* 스크롤바 숨김 */
.stApp::-webkit-scrollbar {
    display: none;
}

/* 상단 패딩 제거 */
.block-container {
    padding-top: 1rem !important;
}

/* 사이드바 숨김 (로그인 페이지에서만) */
.css-1d391kg {
    display: none;
}

/* 헤더 숨김 */
header[data-testid="stHeader"] {
    display: none;
}
</style>

<script>
// 플로팅 파티클 생성 함수
function createParticles() {
    // 기존 파티클 컨테이너가 있으면 제거
    const existingContainer = document.querySelector('.particle-container');
    if (existingContainer) {
        existingContainer.remove();
    }
    
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.position = 'fixed';
    particleContainer.style.top = '0';
    particleContainer.style.left = '0';
    particleContainer.style.width = '100%';
    particleContainer.style.height = '100%';
    particleContainer.style.pointerEvents = 'none';
    particleContainer.style.zIndex = '-1';
    
    // 20개의 파티클 생성
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        particleContainer.appendChild(particle);
    }
    
    document.body.appendChild(particleContainer);
}

// 페이지 로드 시 파티클 생성 (딜레이 추가)
setTimeout(() => {
    if (document.readyState === 'complete') {
        createParticles();
    } else {
        window.addEventListener('load', createParticles);
    }
}, 500);

// Streamlit 컴포넌트 리렌더링 시에도 파티클 재생성
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            setTimeout(createParticles, 100);
        }
    });
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
</script>
"""