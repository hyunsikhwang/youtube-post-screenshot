import streamlit as st
import os
import asyncio
import nest_asyncio
import urllib.parse
from playwright.async_api import async_playwright

# 1. 초기 설정
nest_asyncio.apply()

if not os.path.exists("ms-playwright"):
    os.system("playwright install chromium")

st.set_page_config(page_title="YouTube Post Screenshot", page_icon=":rocket:", layout="centered")

# ==========================================
# [DESIGN] Minimal + Vivid Glow Styling
# ==========================================
st.markdown("""
<style>
    /* 1. 기본 배경: 아주 깔끔한 오프 화이트 (눈이 편안함) */
    [data-testid="stAppViewContainer"] {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    /* 2. 폰트 적용 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif !important; }

    /* 3. 헤더: 군더더기 없는 모던 타이포그래피 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #111111;
        text-align: center;
        margin-top: 20px;
        letter-spacing: -1px;
    }
    .main-header span {
        color: #4361EE; /* Vivid Blue Accent */
    }
    .sub-header {
        text-align: center;
        color: #868e96;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 50px;
    }

    /* 4. 메인 카드 (Clean White Box) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #FFFFFF !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 20px !important;
        padding: 40px !important;
        /* 부드럽지만 명확한 그림자 */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05) !important; 
    }

    /* 5. 입력창: 미니멀하다가 클릭하면 Vivid Glow 발동 */
    .stTextInput > div > div > input {
        background-color: #F8F9FA !important;
        color: #212529 !important;
        border: 2px solid #E9ECEF !important;
        border-radius: 12px !important;
        padding: 12px 15px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        background-color: #FFFFFF !important;
        border-color: #4361EE !important; /* Vivid Blue */
        /* 선명한 글로우 효과 */
        box-shadow: 0 0 15px rgba(67, 97, 238, 0.4) !important; 
    }

    /* 6. 메인 액션 버튼: 가장 강렬한 포인트 (Neon Gradient) */
    .stButton > button {
        width: 100%;
        /* Vivid Blue to Purple Gradient */
        background: linear-gradient(90deg, #4361EE 0%, #7209B7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        /* 버튼 자체가 빛나는 효과 */
        box-shadow: 0 5px 20px rgba(67, 97, 238, 0.4) !important; 
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(114, 9, 183, 0.5) !important;
    }
    
    /* 7. 다운로드 버튼: 깔끔한 아웃라인 스타일 */
    .stDownloadButton > button {
        background: #FFFFFF !important;
        color: #4361EE !important;
        border: 2px solid #4361EE !important;
        border-radius: 12px !important;
        width: 100%;
        font-weight: 700 !important;
        transition: 0.2s;
    }
    .stDownloadButton > button:hover {
        background: #4361EE !important;
        color: #ffffff !important;
        box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3) !important;
    }

    /* 8. X 공유 버튼: 브랜드 컬러(Black) + 은은한 글로우 */
    a[href*="x.com/intent"] {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        background-color: #000000 !important; 
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 700;
        margin-top: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    a[href*="x.com/intent"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        color: #ffffff !important;
    }
    a[href*="x.com/intent"]::before {
        content: "𝕏 "; 
        margin-right: 8px;
        font-size: 1.2rem;
    }

    /* UI 정리 */
    header, footer {visibility: hidden;}
    /* 이미지도 깔끔한 그림자 처리 */
    img { 
        border-radius: 16px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        border: 1px solid #E9ECEF;
    }
    
</style>
""", unsafe_allow_html=True)

# UI Header
st.markdown('<div class="main-header">YouTube <span>Post Capture</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Minimal Design with Vivid Accents</div>', unsafe_allow_html=True)

async def capture_youtube_post(post_url, output_path="post_capture.png"):
    status_container = st.empty()
    status_container.info(f"⚡ URL 분석 중... {post_url}")
    
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
            st.warning(f"⚠️ 로딩 지연 (진행 중): {e}")

        # 스타일 주입 (다크 모드 캡처 유지)
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
                status_container.write("🔽 내용 펼치는 중...")
                await more_button.click()
                await page.wait_for_timeout(1000)
        except: pass

        try:
            await post_locator.wait_for(timeout=10000)
            await post_locator.screenshot(path=output_path, omit_background=True)
            status_container.success(f"✅ 캡처 성공!") 
        except Exception as e:
            status_container.error(f"❌ 오류 발생: {e}")

        await browser.close()
        return output_path


# --- 실행부 ---

# Minimal Style을 위한 깔끔한 컨테이너
with st.container(border=True):
    default_url = "https://t.co/ukaFlldhP9"
    target_url = st.text_input("유튜브 게시글 URL", value="", placeholder=default_url) # 라벨 간소화

    if st.button("🚀 캡처 시작 (Capture)"):
        with st.spinner("⚡ 처리 중입니다..."):
            result_path = asyncio.run(capture_youtube_post(target_url))
            
            if result_path and os.path.exists(result_path):
                st.markdown("---")
                st.image(result_path, caption="Result Preview", use_column_width=True)
                
                # 1. 다운로드 버튼
                with open(result_path, "rb") as file:
                    st.download_button(
                        label="📥 이미지 저장 (Download)",
                        data=file,
                        file_name="youtube_post_capture.png",
                        mime="image/png"
                    )
                
                # 2. X(Twitter) 공유 버튼
                encoded_text = urllib.parse.quote(target_url)
                share_url = f"https://x.com/intent/tweet?text={encoded_text}"
                
                st.link_button("Share on X (이미지 수동 첨부)", share_url)