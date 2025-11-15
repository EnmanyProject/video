"""
비디오 편집기 역재생 기능 Playwright 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_reverse_video():
    """역재생 기능 테스트"""

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
            print("🎬 비디오 편집기 역재생 기능 테스트")
            print("=" * 60)

            # 1. 페이지 접속
            print("\n1️⃣ http://localhost:8000 접속 중...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            # 초기 스크린샷
            page.screenshot(path='test_screenshots/01_initial.png', full_page=True)
            print("📸 초기 화면 스크린샷 저장")

            # 2. 페이지 요소 확인
            print("\n2️⃣ 페이지 요소 확인 중...")

            # 비디오 플레이어 확인
            video_player = page.locator('#videoPlayer')
            assert video_player.is_visible(), "비디오 플레이어가 보이지 않습니다"
            print("✅ 비디오 플레이어 발견")

            # 파일 입력 확인
            file_input = page.locator('#fileInput')
            assert file_input.is_visible(), "파일 입력이 보이지 않습니다"
            print("✅ 파일 입력 발견")

            # 버튼들 확인
            capture_png_btn = page.locator('#capturePngBtn')
            gif_btn = page.locator('#gifBtn')
            reverse_btn = page.locator('#reverseBtn')

            print("✅ PNG 캡처 버튼 발견")
            print("✅ GIF 생성 버튼 발견")
            print("✅ 역재생 버튼 발견")

            # 3. 테스트 비디오 생성 (간단한 HTML 비디오)
            print("\n3️⃣ 테스트 비디오 준비 중...")

            # 사용자에게 비디오 URL 입력
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
            page.screenshot(path='test_screenshots/02_video_loaded.png', full_page=True)
            print("📸 비디오 로드 후 스크린샷 저장")

            # 4. 버튼 활성화 확인
            print("\n4️⃣ 버튼 활성화 확인 중...")

            assert not capture_png_btn.is_disabled(), "PNG 캡처 버튼이 비활성화되어 있습니다"
            print("✅ PNG 캡처 버튼 활성화됨")

            assert not gif_btn.is_disabled(), "GIF 버튼이 비활성화되어 있습니다"
            print("✅ GIF 버튼 활성화됨")

            assert not reverse_btn.is_disabled(), "역재생 버튼이 비활성화되어 있습니다"
            print("✅ 역재생 버튼 활성화됨")

            # 5. 역재생 옵션 패널 열기
            print("\n5️⃣ 역재생 옵션 패널 열기...")
            reverse_btn.click()
            print("✅ 역재생 버튼 클릭")

            time.sleep(1)
            page.screenshot(path='test_screenshots/03_reverse_options.png', full_page=True)
            print("📸 역재생 옵션 패널 스크린샷 저장")

            # 6. 역재생 옵션 확인
            print("\n6️⃣ 역재생 옵션 확인 중...")

            reverse_controls = page.locator('#reverseControls')
            assert reverse_controls.is_visible(), "역재생 옵션 패널이 보이지 않습니다"
            print("✅ 역재생 옵션 패널 표시됨")

            # FPS 입력 확인
            fps_input = page.locator('#reverseFps')
            assert fps_input.is_visible(), "FPS 입력이 보이지 않습니다"
            fps_value = fps_input.input_value()
            print(f"✅ FPS 설정: {fps_value}")

            # 품질 선택 확인
            quality_select = page.locator('#reverseQuality')
            assert quality_select.is_visible(), "품질 선택이 보이지 않습니다"
            quality_value = quality_select.input_value()
            print(f"✅ 품질 설정: {int(quality_value)/1000000}Mbps")

            # 7. 역재생 설정 변경 (30fps, 낮은 품질로 빠른 테스트)
            print("\n7️⃣ 역재생 설정 변경 중 (테스트용: 30fps, 3Mbps)...")
            fps_input.fill('30')
            quality_select.select_option('3000000')
            print("✅ FPS: 30, 품질: 3Mbps로 설정")

            time.sleep(0.5)
            page.screenshot(path='test_screenshots/04_settings_changed.png', full_page=True)
            print("📸 설정 변경 후 스크린샷 저장")

            # 8. 역재생 시작 버튼 확인
            print("\n8️⃣ 역재생 시작 버튼 확인...")
            start_reverse_btn = page.get_by_text('역재생 시작')
            assert start_reverse_btn.is_visible(), "역재생 시작 버튼이 보이지 않습니다"
            print("✅ 역재생 시작 버튼 발견")

            # 9. 역재생 시작 (실제 실행은 시간이 오래 걸리므로 클릭만 확인)
            print("\n9️⃣ 역재생 시작 버튼 클릭 테스트...")
            start_reverse_btn.click()
            print("✅ 역재생 시작 버튼 클릭됨")

            # 상태 메시지 및 진행률 표시 확인
            time.sleep(2)

            status_message = page.locator('#statusMessage')
            if status_message.is_visible():
                status_text = status_message.inner_text()
                print(f"✅ 상태 메시지: {status_text}")

            progress_container = page.locator('#progressContainer')
            if progress_container.is_visible():
                print("✅ 진행률 표시 보임")

            page.screenshot(path='test_screenshots/05_reverse_started.png', full_page=True)
            print("📸 역재생 시작 후 스크린샷 저장")

            # 10초 동안 진행 상황 관찰
            print("\n🔟 10초 동안 진행 상황 관찰 중...")
            for i in range(10):
                time.sleep(1)
                progress_fill = page.locator('#progressFill')
                if progress_fill.is_visible():
                    progress_text = progress_fill.inner_text()
                    print(f"  진행률: {progress_text}")

            page.screenshot(path='test_screenshots/06_reverse_progress.png', full_page=True)
            print("📸 진행 중 스크린샷 저장")

            # 11. 콘솔 로그 확인
            print("\n1️⃣1️⃣ 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지:")
                for msg in console_messages[-10:]:  # 마지막 10개만
                    print(f"  {msg}")
            else:
                print("✅ 콘솔 메시지 없음")

            # 12. 에러 확인
            print("\n1️⃣2️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n" + "=" * 60)
            print("✅ 테스트 완료!")
            print("=" * 60)
            print("\n📁 스크린샷 저장 위치: test_screenshots/")
            print("  - 01_initial.png: 초기 화면")
            print("  - 02_video_loaded.png: 비디오 로드 후")
            print("  - 03_reverse_options.png: 역재생 옵션 패널")
            print("  - 04_settings_changed.png: 설정 변경 후")
            print("  - 05_reverse_started.png: 역재생 시작")
            print("  - 06_reverse_progress.png: 진행 중")

            # 사용자가 결과 확인할 시간
            print("\n⏳ 10초 후 브라우저를 닫습니다...")
            time.sleep(10)

        except AssertionError as e:
            print(f"\n❌ 테스트 실패: {e}")
            page.screenshot(path='test_screenshots/error.png', full_page=True)
            print("📸 에러 스크린샷 저장: test_screenshots/error.png")
            raise

        except Exception as e:
            print(f"\n❌ 예외 발생: {e}")
            page.screenshot(path='test_screenshots/exception.png', full_page=True)
            print("📸 예외 스크린샷 저장: test_screenshots/exception.png")
            raise

        finally:
            browser.close()
            print("\n🔚 브라우저 종료")

if __name__ == "__main__":
    # 스크린샷 디렉토리 생성
    os.makedirs('test_screenshots', exist_ok=True)

    test_reverse_video()
