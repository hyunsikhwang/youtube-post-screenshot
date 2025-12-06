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

st.write("# YouTube Post Screenshot App")

async def capture_youtube_post(post_url, output_path="post_capture.png"):
    st.write(f"🌑⚪ 둥근모서리 다크모드 캡처 시작: {post_url}")
    
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
            st.write(f"⚠️ 페이지 로딩 대기 시간 초과 (계속 진행): {e}")

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
                padding: 25px !important;
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
        # 단순히 시간만 기다리는 것(wait_for_timeout)보다 더 확실한 방법입니다.
        try:
             await page.evaluate("document.fonts.ready")
        except:
             # 혹시 구형 브라우저 등에서 실패할 경우를 대비해 짧은 대기 시간 추가
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
                st.write("🔽 '더 보기' 버튼 발견! 내용을 펼칩니다.")
                await more_button.click()
                await page.wait_for_timeout(1000)
            else:
                st.write("ℹ️ '더 보기' 버튼이 없습니다.")
        except Exception as e:
            st.write(f"⚠️ 더 보기 처리 중 이슈: {e}")

        try:
            await post_locator.wait_for(timeout=10000)
            await post_locator.screenshot(path=output_path, omit_background=True)
            st.write(f"✅ 캡처 완료: {output_path}")
            st.image(output_path) # 캡처된 이미지 화면에 표시
        except Exception as e:
            st.write(f"❌ 캡처 및 저장 오류: {e}")

        await browser.close()
        return output_path

# --- 실행부 ---
target_url = st.text_input("유튜브 게시글 URL 입력", "https://t.co/ukaFlldhP9")

if st.button("캡처 실행"):
    # nest_asyncio가 적용되었으므로 asyncio.run을 안전하게 호출하거나 
    # 이미 루프가 있다면 await로 처리해야 하지만, 
    # Streamlit 최상위 레벨에서는 asyncio.run()이 가장 깔끔합니다.
    asyncio.run(capture_youtube_post(target_url))