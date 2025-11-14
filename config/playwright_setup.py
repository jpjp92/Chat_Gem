"""
Playwright 초기화 헬퍼 모듈
Streamlit Cloud 환경에서 playwright 브라우저 설치를 관리합니다.
"""

import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def ensure_playwright_installed():
    """
    Playwright 브라우저 바이너리가 설치되어 있는지 확인하고,
    필요하면 설치합니다. (Streamlit Cloud 환경용)
    """
    try:
        # 이미 설치되었는지 확인
        from playwright.sync_api import sync_playwright
        
        # Streamlit Cloud 환경 감지
        is_streamlit_cloud = "STREAMLIT" in os.environ and "STREAMLIT_SERVER_HEADLESS" in os.environ
        
        if is_streamlit_cloud:
            logger.info("🎭 Streamlit Cloud 환경 감지. Playwright 체크 중...")
            
            # Chromium이 설치되어 있는지 확인
            chromium_path = os.path.expanduser(
                "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"
            )
            
            import glob
            chrome_exists = glob.glob(chromium_path)
            
            if not chrome_exists:
                logger.info("🎭 Chromium 브라우저가 없습니다. 설치 중...")
                try:
                    # 시간 제한을 두고 설치 시도
                    result = subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5분 제한
                    )
                    
                    if result.returncode == 0:
                        logger.info("✅ Playwright Chromium 설치 완료")
                    else:
                        logger.warning(
                            f"⚠️ Playwright 설치 중 오류: {result.stderr}"
                        )
                        return False
                        
                except subprocess.TimeoutExpired:
                    logger.error("❌ Playwright 설치 시간 초과 (5분)")
                    return False
                except Exception as e:
                    logger.warning(f"⚠️ Playwright 설치 실패: {str(e)}")
                    return False
            else:
                logger.info("✅ Playwright Chromium이 이미 설치되어 있습니다")
        
        return True
        
    except ImportError:
        logger.error("❌ Playwright가 설치되지 않았습니다. requirements.txt 확인 필요")
        return False
    except Exception as e:
        logger.error(f"❌ Playwright 초기화 오류: {str(e)}")
        return False


def disable_playwright_for_streamlit_cloud():
    """
    Streamlit Cloud에서 Playwright가 작동하지 않는 경우를 대비한
    폴백 플래그 설정
    """
    is_streamlit_cloud = "STREAMLIT" in os.environ and "STREAMLIT_SERVER_HEADLESS" in os.environ
    if is_streamlit_cloud:
        os.environ["PLAYWRIGHT_DISABLED"] = "1"
        logger.warning("🎭 Playwright 비활성화 플래그 설정됨")


# 모듈 로드 시 자동 초기화 시도
if __name__ != "__main__":
    try:
        playwright_available = ensure_playwright_installed()
        if not playwright_available:
            disable_playwright_for_streamlit_cloud()
    except Exception as e:
        logger.warning(f"Playwright 자동 초기화 실패: {str(e)}")
