import os
os.system("playwright install")
os.system("playwright install chromium")
os.system("playwright install-deps")

import streamlit as st
from playwright.sync_api import Playwright, sync_playwright, expect
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright


st.write("# YouTube Post Screenshot App")

async def capture_youtube_post(post_url, output_path="post_capture.png"):
    st.write(f"🌑⚪ 둥근모서리 다크모드 캡처 시작: {post_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox'] 
        )
        
        # 고화질(3배), 다크모드 설정
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=3,
            color_scheme='dark',
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = await context.new_page()

        try:
            await page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
        except:
            pass

        # ✨ [CSS 수정] 폰트, 둥근 모서리, 그리고 '글자색 강제 화이트' 적용
        await page.add_style_tag(content="""
            /* 1. 폰트 설정 */
            @font-face { font-family: 'NanumSquare'; src: local('NanumSquare'); }
            * { font-family: 'NanumSquare', sans-serif !important; }
            
            /* 2. 게시글 컨테이너 스타일 (배경 다크, 둥근 모서리) */
            ytd-backstage-post-renderer {
                background-color: #181818 !important;
                border-radius: 24px !important;
                border: 1px solid #333333 !important;
                padding: 25px !important;
                overflow: hidden !important;
            }

            /* 3. [핵심 해결책] 내부의 모든 요소(*)에게 색상 강제 부여 */
            /* 유튜브 자체 변수(--yt-...)와 color 속성을 모두 덮어씁니다 */
            ytd-backstage-post-renderer, 
            ytd-backstage-post-renderer * {
                color: #ffffff !important; /* 기본 글자: 완전 흰색 */
                --yt-spec-text-primary: #ffffff !important;
                --yt-spec-text-secondary: #dddddd !important; /* 날짜 등은 살짝 연한 흰색 */
            }

            /* 4. (옵션) 링크와 해시태그는 포인트 컬러(하늘색)로 유지 */
            ytd-backstage-post-renderer a {
                color: #3ea6ff !important;
                text-decoration: none !important;
            }
        """)

        await page.wait_for_timeout(500)

        # 팝업 닫기
        try:
            await page.click('button[aria-label*="Reject"]', timeout=2000)
        except:
            pass 

        # 요소 선택
        selector = "ytd-backstage-post-renderer"
        post_locator = page.locator(selector).first
        
        try:
            more_button = post_locator.get_by_text("Read more")
            
            # 버튼이 화면에 보이면 클릭 (timeout=3000: 3초만 기다려보고 없으면 넘어감)
            if await more_button.is_visible(timeout=3000):
                st.write("🔽 '더 보기' 버튼 발견! 내용을 펼칩니다.")
                await more_button.click()
                
                # 클릭 후 텍스트가 펼쳐지는 애니메이션 대기 (0.5~1초)
                await page.wait_for_timeout(1000)
            else:
                st.write("ℹ️ '더 보기' 버튼이 없습니다 (짧은 글).")
        except Exception as e:
            # 에러가 나도 스크린샷은 찍어야 하므로 패스
            st.write(f"⚠️ 더 보기 처리 중 경미한 이슈: {e}")

        try:
            await post_locator.wait_for(timeout=10000)
            
            # ✨ [스크린샷 핵심] omit_background=True 로 배경 투명화
            await post_locator.screenshot(
                path=output_path, 
                omit_background=True
            )
            st.write(f"✅ 캡처 완료: {output_path}")
        except Exception as e:
            st.write(f"❌ 오류 발생: {e}")

        await browser.close()
        return output_path

# --- 실행부 ---
# 테스트할 유튜브 커뮤니티 포스트 URL (예시 URL을 실제 URL로 교체하세요)
# 주의: 채널 홈 URL이 아니라, 특정 게시글의 고유 URL이어야 합니다.
target_url = "https://t.co/ukaFlldhP9" 

# Colab은 이미 비동기 환경이므로 asyncio.run() 대신 바로 await를 사용합니다.
# 실제 실행 시에는 아래 주석을 풀고 URL을 입력하세요.
asyncio.run(capture_youtube_post(target_url))