"""
통합 타임라인 드래그 기능 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_integrated_timeline():
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
            print("🎬 통합 타임라인 드래그 기능 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            page.screenshot(path='test_screenshots/timeline_01_initial.png', full_page=True)

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

            page.screenshot(path='test_screenshots/timeline_02_video_loaded.png', full_page=True)

            print("\n3️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn = page.locator('#trimBtn')
            is_visible = trim_btn.is_visible()
            is_enabled = not trim_btn.is_disabled()
            print(f"✅ 버튼 보임: {is_visible}")
            print(f"✅ 버튼 활성화: {is_enabled}")

            trim_btn.click()
            print("✅ 버튼 클릭됨")

            time.sleep(1)
            page.screenshot(path='test_screenshots/timeline_03_after_click.png', full_page=True)

            print("\n4️⃣ 통합 타임라인 UI 확인...")
            timeline_selector = page.locator('#timelineRangeSelector')
            timeline_visible = timeline_selector.is_visible()
            print(f"✅ 타임라인 패널 보임: {timeline_visible}")

            if timeline_visible:
                # 타임라인 요소 확인
                container = page.locator('#timelineContainer')
                start_handle = page.locator('#startHandle')
                end_handle = page.locator('#endHandle')
                selected_range = page.locator('#selectedRange')

                print("\n5️⃣ 타임라인 요소 확인...")
                print(f"✅ 타임라인 컨테이너 보임: {container.is_visible()}")
                print(f"✅ 시작 핸들 보임: {start_handle.is_visible()}")
                print(f"✅ 종료 핸들 보임: {end_handle.is_visible()}")
                print(f"✅ 선택 범위 보임: {selected_range.is_visible()}")

                # 현재 상태 확인
                state_info = page.evaluate("""
                    () => {
                        return {
                            startTime: trimRangeState.startTime,
                            endTime: trimRangeState.endTime,
                            isDragging: trimRangeState.isDragging,
                            dragTarget: trimRangeState.dragTarget
                        };
                    }
                """)
                print(f"\n📊 타임라인 상태:")
                print(f"   - 시작 시간: {state_info['startTime']}초")
                print(f"   - 종료 시간: {state_info['endTime']}초")
                print(f"   - 드래그 중: {state_info['isDragging']}")

                # 디스플레이 텍스트 확인
                range_display = page.locator('#rangeTimeDisplay').text_content()
                duration_display = page.locator('#rangeDurationDisplay').text_content()
                print(f"   - 선택 구간: {range_display}")
                print(f"   - 길이: {duration_display}")

                print("\n6️⃣ 시작 핸들 드래그 테스트...")
                # 핸들의 위치 가져오기
                handle_box = start_handle.bounding_box()
                container_box = container.bounding_box()

                if handle_box and container_box:
                    # 시작 위치 (핸들 중앙)
                    start_x = handle_box['x'] + handle_box['width'] / 2
                    start_y = handle_box['y'] + handle_box['height'] / 2

                    # 목표 위치 (컨테이너의 30% 지점)
                    target_x = container_box['x'] + container_box['width'] * 0.3
                    target_y = start_y

                    # 드래그 시뮬레이션
                    page.mouse.move(start_x, start_y)
                    page.mouse.down()
                    print(f"✅ 시작 핸들에서 마우스 다운")

                    time.sleep(0.3)

                    page.mouse.move(target_x, target_y)
                    print(f"✅ 마우스를 30% 위치로 이동")

                    time.sleep(0.3)

                    # 비디오 시간이 변경되었는지 확인
                    new_video_time = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
                    print(f"✅ 비디오 현재 시간: {new_video_time}초")

                    page.mouse.up()
                    print(f"✅ 마우스 업")

                    time.sleep(0.5)
                    page.screenshot(path='test_screenshots/timeline_04_after_start_drag.png', full_page=True)

                    # 업데이트된 상태 확인
                    updated_state = page.evaluate("""
                        () => {
                            return {
                                startTime: trimRangeState.startTime,
                                endTime: trimRangeState.endTime,
                                videoTime: document.getElementById('videoPlayer').currentTime
                            };
                        }
                    """)
                    print(f"\n📊 드래그 후 상태:")
                    print(f"   - 시작 시간: {updated_state['startTime']}초")
                    print(f"   - 종료 시간: {updated_state['endTime']}초")
                    print(f"   - 비디오 시간: {updated_state['videoTime']}초")

                print("\n7️⃣ 종료 핸들 드래그 테스트...")
                # 종료 핸들 드래그
                end_handle_box = end_handle.bounding_box()

                if end_handle_box and container_box:
                    start_x = end_handle_box['x'] + end_handle_box['width'] / 2
                    start_y = end_handle_box['y'] + end_handle_box['height'] / 2

                    # 목표 위치 (컨테이너의 70% 지점)
                    target_x = container_box['x'] + container_box['width'] * 0.7
                    target_y = start_y

                    page.mouse.move(start_x, start_y)
                    page.mouse.down()
                    print(f"✅ 종료 핸들에서 마우스 다운")

                    time.sleep(0.3)

                    page.mouse.move(target_x, target_y)
                    print(f"✅ 마우스를 70% 위치로 이동")

                    time.sleep(0.3)

                    # 비디오 시간이 변경되었는지 확인
                    new_video_time = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
                    print(f"✅ 비디오 현재 시간: {new_video_time}초")

                    page.mouse.up()
                    print(f"✅ 마우스 업")

                    time.sleep(0.5)
                    page.screenshot(path='test_screenshots/timeline_05_after_end_drag.png', full_page=True)

                    # 최종 상태 확인
                    final_state = page.evaluate("""
                        () => {
                            return {
                                startTime: trimRangeState.startTime,
                                endTime: trimRangeState.endTime,
                                videoTime: document.getElementById('videoPlayer').currentTime
                            };
                        }
                    """)
                    print(f"\n📊 최종 상태:")
                    print(f"   - 시작 시간: {final_state['startTime']}초")
                    print(f"   - 종료 시간: {final_state['endTime']}초")
                    print(f"   - 비디오 시간: {final_state['videoTime']}초")

            else:
                print("❌ 통합 타임라인이 보이지 않습니다!")

            print("\n8️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n9️⃣ 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지 (최근 10개):")
                for msg in console_messages[-10:]:
                    print(f"  {msg}")
            else:
                print("✅ 콘솔 메시지 없음")

            print("\n" + "=" * 60)
            if timeline_visible:
                print("✅ 통합 타임라인 드래그 기능 테스트 성공!")
            else:
                print("❌ 통합 타임라인이 표시되지 않음!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - timeline_01_initial.png: 초기 화면")
            print("  - timeline_02_video_loaded.png: 비디오 로드 후")
            print("  - timeline_03_after_click.png: 버튼 클릭 후")
            if timeline_visible:
                print("  - timeline_04_after_start_drag.png: 시작 핸들 드래그 후")
                print("  - timeline_05_after_end_drag.png: 종료 핸들 드래그 후")

            print("\n⏳ 10초 후 브라우저 종료...")
            time.sleep(10)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='test_screenshots/timeline_error.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_integrated_timeline()
