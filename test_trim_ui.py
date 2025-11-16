"""
구간 잘라내기 UI 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_trim_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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
            print("✂️ 구간 잘라내기 UI 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            page.screenshot(path='test_screenshots/trim_01_initial.png', full_page=True)

            print("\n2️⃣ 테스트 비디오 로드...")
            url_input = page.locator('#urlInput')
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)
            print(f"✅ URL 입력: {test_url}")

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            print("✅ URL 로드 버튼 클릭")

            time.sleep(5)
            print("✅ 비디오 로드 대기 완료")

            # 비디오 duration 확인
            video_info = page.evaluate("""
                () => {
                    const video = document.getElementById('videoPlayer');
                    return {
                        duration: video.duration,
                        readyState: video.readyState,
                        currentTime: video.currentTime
                    };
                }
            """)
            print(f"\n📹 비디오 정보:")
            print(f"   - Duration: {video_info['duration']}초")
            print(f"   - Ready State: {video_info['readyState']}")
            print(f"   - Current Time: {video_info['currentTime']}초")

            page.screenshot(path='test_screenshots/trim_02_video_loaded.png', full_page=True)

            print("\n3️⃣ 구간 잘라내기 버튼 확인...")
            trim_btn = page.locator('#trimBtn')
            is_visible = trim_btn.is_visible()
            is_enabled = not trim_btn.is_disabled()
            print(f"✅ 버튼 보임: {is_visible}")
            print(f"✅ 버튼 활성화: {is_enabled}")

            print("\n4️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn.click()
            print("✅ 버튼 클릭됨")

            time.sleep(1)
            page.screenshot(path='test_screenshots/trim_03_after_click.png', full_page=True)

            print("\n5️⃣ 트림 옵션 패널 확인...")
            trim_controls = page.locator('#trimControls')
            panel_visible = trim_controls.is_visible()
            print(f"✅ 옵션 패널 보임: {panel_visible}")

            if panel_visible:
                # 슬라이더 확인
                start_slider = page.locator('#trimStartTime')
                end_slider = page.locator('#trimEndTime')
                start_num = page.locator('#trimStartTimeNum')
                end_num = page.locator('#trimEndTimeNum')

                print("\n6️⃣ 슬라이더 요소 확인...")
                print(f"✅ 시작 슬라이더 보임: {start_slider.is_visible()}")
                print(f"✅ 종료 슬라이더 보임: {end_slider.is_visible()}")
                print(f"✅ 시작 숫자 입력 보임: {start_num.is_visible()}")
                print(f"✅ 종료 숫자 입력 보임: {end_num.is_visible()}")

                # 현재 값 확인
                start_val = start_slider.input_value()
                end_val = end_slider.input_value()
                print(f"\n현재 값:")
                print(f"  - 시작: {start_val}초")
                print(f"  - 종료: {end_val}초")

                # 표시 텍스트 확인
                range_display = page.locator('#trimRangeDisplay').text_content()
                duration_display = page.locator('#trimDurationDisplay').text_content()
                print(f"  - 선택 구간: {range_display}")
                print(f"  - 길이: {duration_display}")

                print("\n7️⃣ 슬라이더 테스트 (시작 시간 변경)...")
                # 시작 슬라이더를 5초로 변경 (range input은 evaluate 사용)
                page.evaluate("""
                    () => {
                        const slider = document.getElementById('trimStartTime');
                        slider.value = '5';
                        slider.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                """)
                time.sleep(0.5)

                # 업데이트된 값 확인
                new_start = start_slider.input_value()
                new_start_num = start_num.input_value()
                new_range_display = page.locator('#trimRangeDisplay').text_content()
                new_duration_display = page.locator('#trimDurationDisplay').text_content()

                print(f"✅ 시작 슬라이더 값: {new_start}초")
                print(f"✅ 시작 숫자 값: {new_start_num}초")
                print(f"✅ 업데이트된 구간: {new_range_display}")
                print(f"✅ 업데이트된 길이: {new_duration_display}")

                page.screenshot(path='test_screenshots/trim_04_slider_changed.png', full_page=True)

                print("\n8️⃣ 슬라이더 테스트 (종료 시간 변경)...")
                # 종료 슬라이더를 20초로 변경
                page.evaluate("""
                    () => {
                        const slider = document.getElementById('trimEndTime');
                        slider.value = '20';
                        slider.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                """)
                time.sleep(0.5)

                new_end = end_slider.input_value()
                new_end_num = end_num.input_value()
                final_range_display = page.locator('#trimRangeDisplay').text_content()
                final_duration_display = page.locator('#trimDurationDisplay').text_content()

                print(f"✅ 종료 슬라이더 값: {new_end}초")
                print(f"✅ 종료 숫자 값: {new_end_num}초")
                print(f"✅ 최종 구간: {final_range_display}")
                print(f"✅ 최종 길이: {final_duration_display}")

                page.screenshot(path='test_screenshots/trim_05_final_state.png', full_page=True)

            else:
                print("❌ 트림 옵션 패널이 보이지 않습니다!")

            print("\n9️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n🔟 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지 (최근 10개):")
                for msg in console_messages[-10:]:
                    print(f"  {msg}")
            else:
                print("✅ 콘솔 메시지 없음")

            print("\n" + "=" * 60)
            if panel_visible:
                print("✅ 구간 잘라내기 UI 테스트 성공!")
            else:
                print("❌ 구간 잘라내기 UI가 표시되지 않음!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - trim_01_initial.png: 초기 화면")
            print("  - trim_02_video_loaded.png: 비디오 로드 후")
            print("  - trim_03_after_click.png: 버튼 클릭 후")
            if panel_visible:
                print("  - trim_04_slider_changed.png: 시작 슬라이더 변경")
                print("  - trim_05_final_state.png: 최종 상태")

            print("\n⏳ 10초 후 브라우저 종료...")
            time.sleep(10)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='test_screenshots/trim_error.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_trim_ui()
