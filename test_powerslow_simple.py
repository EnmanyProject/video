"""
파워슬로우 기능 간단 검증
- 콘솔 로그 모니터링
- 프레임 보간 동작 확인
"""
from playwright.sync_api import sync_playwright
import time

def test_powerslow_console():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        # 콘솔 로그 수집
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("📖 페이지 로드 중...")
        page.goto('https://enmanyproject.github.io/video/')
        page.wait_for_load_state('networkidle')

        print("✅ 페이지 로드 완료")
        print("\n" + "="*70)
        print("🎬 브라우저가 열렸습니다!")
        print("📹 다음 작업을 수행해주세요:")
        print("   1. 비디오를 로드하세요 (로컬 파일 또는 URL)")
        print("   2. 비디오를 재생하세요")
        print("   3. '⚡ 파워슬로우 재생 OFF' 버튼을 클릭하세요")
        print("   4. 5-10초 정도 슬로우 모션 재생을 관찰하세요")
        print("   5. 다시 버튼을 클릭하여 OFF로 전환하세요")
        print("\n💡 관찰 포인트:")
        print("   - 슬로우 모션이 '부드럽게' 느껴지는지?")
        print("   - 아니면 그냥 '느리게만' 느껴지는지?")
        print("="*70)

        # 60초 동안 관찰 시간 제공
        for i in range(60, 0, -1):
            print(f"\r⏳ 테스트 진행 중... {i}초 남음 (자유롭게 테스트하세요)  ", end='', flush=True)
            time.sleep(1)

        print("\n\n📊 수집된 콘솔 로그 (마지막 30개):")
        print("-" * 70)
        for log in console_logs[-30:]:
            print(f"  {log}")
        print("-" * 70)

        # 최종 스크린샷
        page.screenshot(path='test_powerslow_final.png', full_page=True)
        print("\n📸 최종 스크린샷 저장: test_powerslow_final.png")

        browser.close()
        print("\n✅ 테스트 완료!")
        print("\n📝 결과 요약:")
        print("   - 브라우저에서 직접 슬로우 모션의 품질을 확인하셨습니다")
        print("   - 부드러움이 느껴지지 않았다면 프레임 보간 알고리즘 개선이 필요합니다")

if __name__ == '__main__':
    test_powerslow_console()
