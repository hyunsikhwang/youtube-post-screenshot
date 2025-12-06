import streamlit as st
import os
import asyncio
import nest_asyncio
import urllib.parse # URL 인코딩을 위해 추가
from playwright.async_api import async_playwright

# 1. 초기 설정
nest_asyncio.apply()

if not os.path.exists("ms-playwright"):
    os.system("playwright install chromium")

st.set_page_config(page_title="YouTube Post Screenshot", page_icon=":rocket:", layout="centered")

# ==========================================
# [DESIGN] Bright Liquid Glass & Modern UI Styling
# ==========================================
st.markdown("""
<style>
    /* 1. 전체 배경 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #e0c3fc, #8ec5fc, #e0c3fc, #cfdef3);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #333333;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. 폰트 적용 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    /* 3. 헤더 디자인 */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 10px 30px rgba(37, 117, 252, 0.2); 
    }
    .sub-header {
        text-align: center;
        color: #555555;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }

    /* 4. Glass Card Container */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        padding: 35px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important; 
    }

    /* 5. Input Field Styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: #333333 !important;
        border: 1px solid rgba(200, 200, 200, 0.5) !important;
        border-radius: 16px !important;
        padding: 12px 15px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2575fc !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(37, 117, 252, 0.2) !important;
    }

    /* 6. Main Action Button (Gradient) */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 20px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(37, 117, 252, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(37, 117, 252, 0.4) !important;
    }
    
    /* 7. Download Button (Outline Blue) */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.6) !important;
        color: #2575fc !important;
        border: 2px solid #2575fc !important;
        border-radius: 16px !important;
        width: 100%;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    .stDownloadButton > button:hover {
        background: #2575fc !important;
        color: #ffffff !important;
    }

    /* 8. X Share Button Styling (Link Button) */
    /* Streamlit Link Button은 a 태그로 렌더링되므로 이를 타겟팅 */
    a[href*="x.com/intent"] {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        background-color: #000000 !important; /* X Brand Color */
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 16px;
        padding: 12px 20px;
        font-weight: 700;
        margin-top: 10px;
        transition: transform 0.2s;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border: 1px solid #333333;
    }
    a[href*="x.com/intent"]:hover {
        transform: translateY(-2px);
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    a[href*="x.com/intent"]::before {
        content: "𝕏 "; /* Unicode X logo styling */
        margin-right: 8px;
        font-size: 1.2rem;
    }

    /* UI 정리 */
    header, footer {visibility: hidden;}
    img { border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); border: 4px solid #ffffff; margin-bottom: 20px;}
    
</style>
""", unsafe_allow_html=True)

# UI Header
st.markdown('<div class="main-header">YouTube Post Capture</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Premium Bright Mode & Glass Design</div>', unsafe_allow_html=True)

async def capture_youtube_post(post_url, output_path="post_capture.png"):
    status_container = st.empty()
    status_container.info(f"🔄 캡처 프로세스 시작... {post_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
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
            st.warning(f"⚠️ 페이지 로딩 이슈 (계속 진행): {e}")

        # 스타일 주입 (기존 유지)
        await page.add_style_tag(content="""
            ytd-masthead, #masthead-container { display: none !important; visibility: hidden !important; height: 0 !important; }
            ytd-app #page-manager.ytd-app { margin-top: 0 !important; }
            @font-face { font-family: 'NanumSquare'; src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@master/NanumSquareR.woff2') format('woff2'); }
            @font-face { font-family: 'NanumSquare'; font-weight: 700; src: url('https://cdn.jsdelivr.net/gh/moonspam/NanumSquare@master/NanumSquareB.woff2') format('woff2'); }
            * { font-family: 'NanumSquare', sans-serif !important; }
            ytd-backstage-post-renderer {
                background-color: #181818 !important; border-radius: 24px !important;
                border: 1px solid #333333 !important; padding: 20px !important;
                margin: 20px auto !important; display: block !important;
            }
            ytd-backstage-post-renderer, ytd-backstage-post-renderer * {
                color: #ffffff !important; --yt-spec-text-primary: #ffffff !important; --yt-spec-text-secondary: #dddddd !important;
            }
            ytd-backstage-post-renderer a, ytd-backstage-post-renderer span[class*="hashtag"] {
                color: #3ea6ff !important; text-decoration: none !important;
            }
        """)

        try: await page.evaluate("document.fonts.ready")
        except: await page.wait_for_timeout(2000)

        try:
            if await page.locator('button[aria-label*="Reject"]').is_visible():
                 await page.click('button[aria-label*="Reject"]')
        except: pass 

        selector = "ytd-backstage-post-renderer"
        post_locator = page.locator(selector).first
        
        try:
            more_button = post_locator.get_by_text("Read more")
            if await more_button.is_visible(timeout=3000):
                status_container.write("🔽 '더 보기' 버튼 발견! 내용을 펼칩니다.")
                await more_button.click()
                await page.wait_for_timeout(1000)
        except: pass

        try:
            await post_locator.wait_for(timeout=10000)
            await post_locator.screenshot(path=output_path, omit_background=True)
            status_container.success(f"✅ 캡처 완료!") 
        except Exception as e:
            status_container.error(f"❌ 캡처 및 저장 오류: {e}")

        await browser.close()
        return output_path


# --- 실행부 ---

with st.container(border=True):
    default_url = "https://t.co/ukaFlldhP9"
    target_url = st.text_input("유튜브 게시글 URL 입력", default_url)

    if st.button("🚀 캡처 실행"):
        with st.spinner("✨ 캡처를 준비하고 있습니다..."):
            result_path = asyncio.run(capture_youtube_post(target_url))
            
            if result_path and os.path.exists(result_path):
                st.markdown("---")
                st.image(result_path, caption="Capture Result", use_column_width=True)
                
                # 1. 다운로드 버튼
                with open(result_path, "rb") as file:
                    st.download_button(
                        label="📥 이미지 다운로드 (PNG)",
                        data=file,
                        file_name="youtube_post_capture.png",
                        mime="image/png"
                    )
                
                # 2. X(Twitter) 공유 버튼 구성
                # 텍스트 인코딩
                encoded_text = urllib.parse.quote(target_url)
                # X Intent URL 생성
                share_url = f"https://x.com/intent/tweet?text={encoded_text}"
                
                # 공유 버튼 (CSS로 스타일링됨)
                st.link_button("Share on X (이미지 붙여넣기 필요)", share_url)
                
                # 안내 문구 (작게)
                st.caption("ℹ️ 보안 정책상 이미지는 자동 첨부되지 않습니다. 다운로드한 이미지를 X 게시글 창에 직접 추가해주세요.")