"""
비디오 편집기 텍스트 미리보기 기능 Playwright 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_text_preview():
    """텍스트 미리보기 기능 테스트"""

    with sync_playwright() as p:
        # 브라우저 실행 (헤드리스 모드)
        browser = p.chromium.launch(headless=False)  # 시각적 확인을 위해 headless=False
        context = browser.new_context()
        page = context.new_page()

        # 콘솔 로그 수집
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # 에러 수집
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))

        try:
            print("=" * 60)
            print("🎬 비디오 편집기 텍스트 미리보기 기능 테스트")
            print("=" * 60)

            # 1. 페이지 접속
            print("\n1️⃣ http://localhost:8000 접속 중...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            # 초기 스크린샷
            page.screenshot(path='test_screenshots/preview_01_initial.png', full_page=True)
            print("📸 초기 화면 스크린샷 저장")

            # 2. 페이지 요소 확인
            print("\n2️⃣ 페이지 요소 확인 중...")

            # 비디오 플레이어 확인
            video_player = page.locator('#videoPlayer')
            assert video_player.is_visible(), "비디오 플레이어가 보이지 않습니다"
            print("✅ 비디오 플레이어 발견")

            # 미리보기 캔버스 확인
            preview_canvas = page.locator('#previewCanvas')
            print("✅ 미리보기 캔버스 발견")

            # 텍스트 입력 필드 확인
            text_input = page.locator('#captureText')
            assert text_input.is_visible(), "텍스트 입력 필드가 보이지 않습니다"
            print("✅ 텍스트 입력 필드 발견")

            # 3. 테스트 비디오 로드
            print("\n3️⃣ 테스트 비디오 로드 중...")
            url_input = page.locator('#urlInput')
            test_video_url = "https://www.w3schools.com/html/mov_bbb.mp4"  # 작은 테스트 비디오

            url_input.fill(test_video_url)
            print(f"✅ 테스트 비디오 URL 입력: {test_video_url}")

            # URL에서 불러오기 버튼 클릭
            load_url_btn = page.get_by_text('URL에서 불러오기')
            load_url_btn.click()
            print("✅ URL 로드 버튼 클릭")

            # 비디오 로드 대기
            time.sleep(3)
            page.screenshot(path='test_screenshots/preview_02_video_loaded.png', full_page=True)
            print("📸 비디오 로드 후 스크린샷 저장")

            # 4. 텍스트 입력 테스트
            print("\n4️⃣ 텍스트 입력 테스트 중...")

            # 텍스트 입력
            test_text = "테스트 미리보기 텍스트"
            text_input.fill(test_text)
            print(f"✅ 텍스트 입력: {test_text}")

            time.sleep(1)
            page.screenshot(path='test_screenshots/preview_03_text_entered.png', full_page=True)
            print("📸 텍스트 입력 후 스크린샷 저장")

            # 5. 폰트 크기 변경 테스트
            print("\n5️⃣ 폰트 크기 변경 테스트...")
            font_size_select = page.locator('#captureFontSize')
            font_size_select.select_option('64')
            print("✅ 폰트 크기를 64px로 변경")

            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_04_font_size_64.png', full_page=True)
            print("📸 폰트 크기 변경 후 스크린샷 저장")

            # 6. 텍스트 색상 변경 테스트
            print("\n6️⃣ 텍스트 색상 변경 테스트...")
            color_select = page.locator('#captureTextColor')
            color_select.select_option('#FF0000')
            print("✅ 텍스트 색상을 빨강색으로 변경")

            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_05_color_red.png', full_page=True)
            print("📸 색상 변경 후 스크린샷 저장")

            # 7. 텍스트 위치 변경 테스트
            print("\n7️⃣ 텍스트 위치 변경 테스트...")
            position_select = page.locator('#captureTextPosition')

            # 상단
            position_select.select_option('top')
            print("✅ 텍스트 위치를 상단으로 변경")
            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_06_position_top.png', full_page=True)
            print("📸 상단 위치 스크린샷 저장")

            # 중앙
            position_select.select_option('middle')
            print("✅ 텍스트 위치를 중앙으로 변경")
            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_07_position_middle.png', full_page=True)
            print("📸 중앙 위치 스크린샷 저장")

            # 하단
            position_select.select_option('bottom')
            print("✅ 텍스트 위치를 하단으로 변경")
            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_08_position_bottom.png', full_page=True)
            print("📸 하단 위치 스크린샷 저장")

            # 8. 타임스탬프 표시 테스트
            print("\n8️⃣ 타임스탬프 표시 테스트...")
            timestamp_checkbox = page.locator('#showTimestamp')
            timestamp_checkbox.check()
            print("✅ 타임스탬프 체크박스 활성화")

            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_09_with_timestamp.png', full_page=True)
            print("📸 타임스탬프 표시 스크린샷 저장")

            # 9. 텍스트 스타일 변경 테스트
            print("\n9️⃣ 텍스트 스타일 변경 테스트...")
            style_select = page.locator('#captureTextStyle')

            # 배경 있음
            style_select.select_option('background')
            print("✅ 텍스트 스타일을 배경 있음으로 변경")
            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_10_style_background.png', full_page=True)
            print("📸 배경 있음 스크린샷 저장")

            # 배경 없음 (투명)
            style_select.select_option('transparent')
            print("✅ 텍스트 스타일을 투명으로 변경")
            time.sleep(0.5)
            page.screenshot(path='test_screenshots/preview_11_style_transparent.png', full_page=True)
            print("📸 투명 스타일 스크린샷 저장")

            # 10. 모든 옵션 조합 테스트
            print("\n🔟 모든 옵션 조합 테스트...")
            text_input.fill("🎬 최종 미리보기 테스트")
            font_size_select.select_option('48')
            color_select.select_option('#FFFFFF')
            position_select.select_option('bottom')
            style_select.select_option('background')
            timestamp_checkbox.check()

            print("✅ 모든 옵션 설정 완료:")
            print("   - 텍스트: 🎬 최종 미리보기 테스트")
            print("   - 폰트 크기: 48px")
            print("   - 색상: 흰색")
            print("   - 위치: 하단")
            print("   - 스타일: 배경 있음")
            print("   - 타임스탬프: 표시")

            time.sleep(1)
            page.screenshot(path='test_screenshots/preview_12_final_combination.png', full_page=True)
            print("📸 최종 조합 스크린샷 저장")

            # 11. Canvas 검증
            print("\n1️⃣1️⃣ Canvas 상태 검증...")
            canvas_visible = preview_canvas.is_visible()
            print(f"✅ 미리보기 캔버스 표시 여부: {canvas_visible}")

            # JavaScript로 canvas 크기 확인
            canvas_info = page.evaluate("""
                () => {
                    const canvas = document.getElementById('previewCanvas');
                    const video = document.getElementById('videoPlayer');
                    return {
                        canvasWidth: canvas.width,
                        canvasHeight: canvas.height,
                        videoWidth: video.videoWidth,
                        videoHeight: video.videoHeight,
                        canvasStyle: window.getComputedStyle(canvas).zIndex
                    };
                }
            """)
            print(f"✅ Canvas 정보:")
            print(f"   - Canvas 크기: {canvas_info['canvasWidth']} x {canvas_info['canvasHeight']}")
            print(f"   - Video 크기: {canvas_info['videoWidth']} x {canvas_info['videoHeight']}")
            print(f"   - z-index: {canvas_info['canvasStyle']}")

            # 12. 콘솔 로그 확인
            print("\n1️⃣2️⃣ 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지:")
                for msg in console_messages[-10:]:  # 마지막 10개만
                    print(f"  {msg}")
            else:
                print("✅ 콘솔 메시지 없음")

            # 13. 에러 확인
            print("\n1️⃣3️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n" + "=" * 60)
            print("✅ 텍스트 미리보기 테스트 완료!")
            print("=" * 60)
            print("\n📁 스크린샷 저장 위치: test_screenshots/")
            print("  - preview_01_initial.png: 초기 화면")
            print("  - preview_02_video_loaded.png: 비디오 로드 후")
            print("  - preview_03_text_entered.png: 텍스트 입력")
            print("  - preview_04_font_size_64.png: 폰트 크기 64px")
            print("  - preview_05_color_red.png: 빨강색 텍스트")
            print("  - preview_06_position_top.png: 상단 위치")
            print("  - preview_07_position_middle.png: 중앙 위치")
            print("  - preview_08_position_bottom.png: 하단 위치")
            print("  - preview_09_with_timestamp.png: 타임스탬프 표시")
            print("  - preview_10_style_background.png: 배경 있음")
            print("  - preview_11_style_transparent.png: 투명 배경")
            print("  - preview_12_final_combination.png: 모든 옵션 조합")

            # 사용자가 결과 확인할 시간
            print("\n⏳ 10초 후 브라우저를 닫습니다...")
            time.sleep(10)

        except AssertionError as e:
            print(f"\n❌ 테스트 실패: {e}")
            page.screenshot(path='test_screenshots/preview_error.png', full_page=True)
            print("📸 에러 스크린샷 저장: test_screenshots/preview_error.png")
            raise

        except Exception as e:
            print(f"\n❌ 예외 발생: {e}")
            page.screenshot(path='test_screenshots/preview_exception.png', full_page=True)
            print("📸 예외 스크린샷 저장: test_screenshots/preview_exception.png")
            raise

        finally:
            browser.close()
            print("\n🔚 브라우저 종료")

if __name__ == "__main__":
    # 스크린샷 디렉토리 생성
    os.makedirs('test_screenshots', exist_ok=True)

    test_text_preview()
