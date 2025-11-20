"""
비디오 갤러리 썸네일 생성 테스트
"""
from playwright.sync_api import sync_playwright
import time

def test_thumbnail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        # 콘솔 로그 수집
        console_logs = []
        errors = []

        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on('pageerror', lambda exc: errors.append(f"[ERROR] {exc}"))

        print("📖 페이지 로드 중...")
        page.goto('http://localhost:8000')
        page.wait_for_load_state('networkidle')

        print("✅ 페이지 로드 완료")
        print("\n" + "="*70)
        print("🎬 브라우저가 열렸습니다!")
        print("📂 다음 작업을 수행해주세요:")
        print("   1. '📂 비디오 폴더 열기' 버튼 클릭")
        print("   2. 비디오 파일이 있는 폴더 선택")
        print("   3. 썸네일이 생성되는지 확인")
        print("\n💡 확인 사항:")
        print("   - 로딩 플레이스홀더(🔄 로딩중...)가 먼저 표시되나?")
        print("   - 썸네일이 실제 비디오 프레임으로 교체되나?")
        print("   - 콘솔에 '✅ 썸네일 생성 완료' 메시지가 나타나나?")
        print("="*70)

        # 60초 동안 관찰 시간 제공
        for i in range(60, 0, -1):
            print(f"\r⏳ 테스트 진행 중... {i}초 남음  ", end='', flush=True)
            time.sleep(1)

        print("\n\n📊 수집된 콘솔 로그:")
        print("-" * 70)
        for log in console_logs[-50:]:  # 마지막 50개만
            print(f"  {log}")
        print("-" * 70)

        if errors:
            print("\n❌ 발견된 에러:")
            print("-" * 70)
            for error in errors:
                print(f"  {error}")
            print("-" * 70)
        else:
            print("\n✅ 에러 없음")

        # 최종 스크린샷
        page.screenshot(path='test_thumbnail_result.png', full_page=True)
        print("\n📸 최종 스크린샷 저장: test_thumbnail_result.png")

        browser.close()
        print("\n✅ 테스트 완료!")

if __name__ == '__main__':
    test_thumbnail()
