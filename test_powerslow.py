"""
파워슬로우 재생 기능 테스트
수동 모드: 브라우저가 열리면 비디오를 수동으로 로드한 후 Enter를 누르세요
"""
from playwright.sync_api import sync_playwright
import time

def test_powerslow():
    with sync_playwright() as p:
        # 브라우저 실행 (headless=False로 실제 화면 보기)
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        # 페이지 로드
        print("📖 페이지 로드 중...")
        page.goto('http://localhost:8000')
        page.wait_for_load_state('networkidle')

        # 초기 스크린샷
        page.screenshot(path='test_powerslow_01_initial.png', full_page=True)
        print("✅ 초기 페이지 로드 완료")

        # 사용자가 수동으로 비디오를 로드하도록 안내
        print("\n" + "="*60)
        print("🎬 브라우저가 열렸습니다!")
        print("📹 30초 안에 비디오를 수동으로 로드해주세요:")
        print("   - URL 입력 또는 로컬 파일 선택")
        print("   - 비디오 로드 후 재생 시작")
        print("="*60)

        for i in range(30, 0, -1):
            print(f"\r⏳ 대기 중... {i}초 남음  ", end='', flush=True)
            time.sleep(1)
        print()

        page.screenshot(path='test_powerslow_02_video_loaded.png', full_page=True)
        print("✅ 비디오 로드 대기 완료")

        video = page.locator('#videoPlayer')

        # 파워슬로우 버튼 찾기
        print("⚡ 파워슬로우 버튼 찾는 중...")
        powerslow_btn = page.locator('#powerSlowToggleBtn')

        if not powerslow_btn.is_enabled():
            print("❌ 파워슬로우 버튼이 비활성화되어 있습니다")
            browser.close()
            return

        print("✅ 파워슬로우 버튼 활성화됨")

        # 비디오 재생
        print("▶️ 비디오 재생 시작...")
        video.evaluate('el => el.play()')
        time.sleep(1)

        # 파워슬로우 ON
        print("⚡ 파워슬로우 ON...")
        page.screenshot(path='test_powerslow_03_before_powerslow.png', full_page=True)
        powerslow_btn.click()
        time.sleep(0.5)

        # 파워슬로우 ON 상태 스크린샷
        page.screenshot(path='test_powerslow_04_powerslow_on.png', full_page=True)
        print("✅ 파워슬로우 ON 완료")

        # 버튼 텍스트 확인
        btn_text = powerslow_btn.inner_text()
        print(f"📊 버튼 텍스트: {btn_text}")

        # 콘솔 로그 모니터링
        print("\n📊 콘솔 로그 수집 중...")
        logs = []
        page.on('console', lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        # 5초간 재생 관찰
        print("⏱️ 5초간 파워슬로우 재생 관찰...")
        for i in range(5):
            time.sleep(1)
            print(f"  {i+1}초 경과...")

        # 최종 스크린샷
        page.screenshot(path='test_powerslow_05_after_5sec.png', full_page=True)

        # 파워슬로우 OFF
        print("\n⚡ 파워슬로우 OFF...")
        powerslow_btn.click()
        time.sleep(0.5)
        page.screenshot(path='test_powerslow_06_powerslow_off.png', full_page=True)

        # 수집된 로그 출력
        print("\n📋 콘솔 로그:")
        for log in logs[-20:]:  # 마지막 20개만
            print(f"  {log}")

        # 5초 더 대기 (결과 확인용)
        print("\n⏸️ 5초간 결과 확인 대기...")
        time.sleep(5)

        browser.close()
        print("\n✅ 테스트 완료!")
        print("📸 스크린샷 저장:")
        print("  - test_powerslow_01_initial.png")
        print("  - test_powerslow_02_video_loaded.png")
        print("  - test_powerslow_03_before_powerslow.png")
        print("  - test_powerslow_04_powerslow_on.png")
        print("  - test_powerslow_05_after_5sec.png")
        print("  - test_powerslow_06_powerslow_off.png")

if __name__ == '__main__':
    test_powerslow()
