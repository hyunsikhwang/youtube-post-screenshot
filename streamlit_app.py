import streamlit as st
import os
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

# 1. 초기 설정: 비동기 루프 패치 및 브라우저 설치
nest_asyncio.apply()  # Streamlit의 루프와 충돌 방지

# 시스템 레벨 설치(install-deps)는 packages.txt가 처리하므로 삭제합니다.
# 브라우저 바이너리(chromium)는 파이썬 레벨에서 설치가 필요할 수 있습니다.
if not os.path.exists("ms-playwright"): # 중복 설치 방지용 체크 (선택사항)
    os.system("playwright install chromium")

st.set_page_config(page_title="YouTube Post Screenshot", page_icon=":rocket:", layout="centered")

# ==========================================
# [DESIGN] Liquid Glass & Modern UI Styling
# ==========================================
st.markdown("""
<style>
    /* 1. 전체 배경: 딥한 다크 그라데이션 & 애니메이션 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #141E30);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #ffffff;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. 폰트 적용 (Pretendard / NanumSquare) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * {
        font-family: 'Pretendard', sans-serif !important;
    }

    /* 3. 헤더 (Liquid Text Effect) */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(0, 198, 255, 0.3);
    }
    .sub-header {
        text-align: center;
        color: #cfd8dc;
        font-size: 1rem;
        margin-bottom: 40px;
        opacity: 0.8;
    }

    /* 4. Glassmorphism Card (입력창 컨테이너) */
    .glass-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* 5. Input Field Styling */
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00c6ff !important;
        box-shadow: 0 0 10px rgba(0, 198, 255, 0.5) !important;
    }
    .stTextInput label {
        color: #e0e0e0 !important;
        font-weight: 600;
    }

    /* 6. Button Styling (Neon Glow) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.6) !important;
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* 7. Download Button Styling */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #00c6ff !important;
        border: 1px solid #00c6ff !important;
        border-radius: 12px !important;
        width: 100%;
        transition: 0.3s;
    }
    .stDownloadButton > button:hover {
        background: rgba(0, 198, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.3) !important;
    }

    /* 8. Spinner & Text styles */
    .stSpinner > div {
        border-top-color: #00c6ff !important;
    }
    
    /* 9. Image Border */
    img {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* 불필요한 상단 바 제거 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# UI Header
st.markdown('<div class="main-header">YouTube Post Capture</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Premium Dark Mode & Rounded Corners</div>', unsafe_allow_html=True)

async def capture_youtube_post(post_url, output_path="post_capture.png"):
    # UI 피드백을 깔끔하게 보여주기 위해 Container 사용
    status_container = st.empty()
    status_container.info(f"🔄 캡처 프로세스 시작... {post_url}")
    
    async with async_playwright() as p:
        # Streamlit Cloud에서는 headless=True 및 sandbox 비활성화 필수
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox'] 
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=3,
            color_scheme='dark',
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            st.warning(f"⚠️ 페이지 로딩 대기 시간 초과 (계속 진행): {e}")

        # ✨ [CSS 수정] 상단바 숨김, 폰트(웹폰트), 둥근 모서리, 색상 강제 적용
        await page.add_style_tag(content="""
            /* -------------------------------------------------------
               0. [핵심 해결책] 상단 검색창(Masthead) 숨기기
            ------------------------------------------------------- */
            ytd-masthead, #masthead-container {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }
            /* 상단바가 사라진 공간만큼 전체 페이지 컨테이너를 위로 올립니다 */
            ytd-app #page-manager.ytd-app {
                margin-top: 0 !important;
            }

            /* -------------------------------------------------------
               1. 나눔스퀘어 웹폰트 정의 및 적용
            ------------------------------------------------------- */
            @font-face {
                font-family: 'NanumSquare';
                font-weight: 400;
                font-style: normal;
                src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@master/NanumSquareR.woff2') format('woff2');
            }
            @font-face {
                font-family: 'NanumSquare';
                font-weight: 700;
                font-style: normal;
                src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@master/NanumSquareB.woff2') format('woff2');
            }
            * { font-family: 'NanumSquare', sans-serif !important; }
            
            /* -------------------------------------------------------
               2. 게시글 컨테이너 스타일
            ------------------------------------------------------- */
            ytd-backstage-post-renderer {
                background-color: #181818 !important;
                border-radius: 24px !important;
                border: 1px solid #333333 !important;
                padding: 20px !important;
                overflow: hidden !important;
                /* 상단바가 없어졌으므로 최상단에 딱 붙지 않게 약간의 여백을 줍니다 */
                margin: 20px auto !important; 
                display: block !important; /* 요소가 제대로 영역을 잡도록 설정 */
            }

            /* -------------------------------------------------------
               3. 내부 요소 색상 강제 부여 (화이트)
            ------------------------------------------------------- */
            ytd-backstage-post-renderer, 
            ytd-backstage-post-renderer * {
                color: #ffffff !important; 
                --yt-spec-text-primary: #ffffff !important;
                --yt-spec-text-secondary: #dddddd !important;
            }

            /* 4. 링크 및 해시태그 색상 유지 */
            ytd-backstage-post-renderer a,
            ytd-backstage-post-renderer span[class*="hashtag"] {
                color: #3ea6ff !important;
                text-decoration: none !important;
            }
        """)

        # 폰트가 다운로드되고 적용될 시간을 줍니다.
        try:
             await page.evaluate("document.fonts.ready")
        except:
             await page.wait_for_timeout(2000)

        # 팝업 닫기 시도
        try:
            if await page.locator('button[aria-label*="Reject"]').is_visible():
                 await page.click('button[aria-label*="Reject"]')
        except:
            pass 

        selector = "ytd-backstage-post-renderer"
        post_locator = page.locator(selector).first
        
        try:
            more_button = post_locator.get_by_text("Read more")
            if await more_button.is_visible(timeout=3000):
                status_container.write("🔽 '더 보기' 버튼 발견! 내용을 펼칩니다.")
                await more_button.click()
                await page.wait_for_timeout(1000)
            else:
                pass # 조용히 넘어감
        except Exception as e:
            st.warning(f"⚠️ 더 보기 처리 중 이슈: {e}")

        try:
            await post_locator.wait_for(timeout=10000)
            await post_locator.screenshot(path=output_path, omit_background=True)
            status_container.success(f"✅ 캡처 완료!") # 경로 노출 대신 심플한 메시지
            # 이미지 표시는 메인 루프에서 처리
        except Exception as e:
            status_container.error(f"❌ 캡처 및 저장 오류: {e}")

        await browser.close()
        return output_path


# --- 실행부 ---

# Glass Card 안에 UI 요소 배치
st.markdown('<div class="glass-container">', unsafe_allow_html=True)

default_url = "https://t.co/ukaFlldhP9"
target_url = st.text_input("유튜브 게시글 URL 입력", default_url)

if st.button("🚀 캡처 실행"):
    with st.spinner("✨ 캡처를 준비하고 있습니다..."):
        # 1. 캡처 함수 실행
        result_path = asyncio.run(capture_youtube_post(target_url))
        
        # 2. 결과 파일이 존재하면 이미지 표시 및 다운로드 버튼 생성
        if result_path and os.path.exists(result_path):
            st.markdown("---")
            # (1) 이미지 화면 표시
            st.image(result_path, caption="Capture Result", use_column_width=True)
            
            # (2) 다운로드 버튼 추가
            with open(result_path, "rb") as file:
                btn = st.download_button(
                    label="📥 이미지 다운로드 (PNG)",
                    data=file,
                    file_name="youtube_post_capture.png",
                    mime="image/png"
                )
st.markdown('</div>', unsafe_allow_html=True)