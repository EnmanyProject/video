"""
드래그 기능 및 타임라인 너비 수정 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_drag_and_width():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 콘솔 로그 수집
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # 에러 수집
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))

        try:
            print("=" * 60)
            print("🎯 드래그 기능 및 타임라인 너비 수정 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            print("\n2️⃣ 테스트 비디오 로드...")
            url_input = page.locator('#urlInput')
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            print("✅ URL 로드 버튼 클릭")

            time.sleep(5)
            print("✅ 비디오 로드 대기 완료")

            # 비디오 정보 확인
            video_info = page.evaluate("""
                () => {
                    const video = document.getElementById('videoPlayer');
                    return {
                        width: video.offsetWidth,
                        readyState: video.readyState,
                        duration: video.duration
                    };
                }
            """)
            print(f"\n📹 비디오 정보:")
            print(f"   - 너비: {video_info['width']}px")
            print(f"   - Ready State: {video_info['readyState']}")
            print(f"   - Duration: {video_info['duration']}초")

            print("\n3️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn = page.locator('#trimBtn')
            trim_btn.click()
            print("✅ 버튼 클릭됨")

            time.sleep(1)

            print("\n4️⃣ 타임라인 너비 확인...")
            timeline_info = page.evaluate("""
                () => {
                    const video = document.getElementById('videoPlayer');
                    const timeline = document.getElementById('timelineContainer');
                    return {
                        videoWidth: video.offsetWidth,
                        timelineWidth: timeline.offsetWidth,
                        timelineStyle: timeline.style.width
                    };
                }
            """)

            print(f"✅ 비디오 플레이어 너비: {timeline_info['videoWidth']}px")
            print(f"✅ 타임라인 너비: {timeline_info['timelineWidth']}px")
            print(f"✅ 타임라인 스타일: {timeline_info['timelineStyle']}")

            if timeline_info['videoWidth'] == timeline_info['timelineWidth']:
                print("✅ 타임라인과 비디오 너비가 동일합니다!")
            else:
                print(f"⚠️ 너비 차이: {abs(timeline_info['videoWidth'] - timeline_info['timelineWidth'])}px")

            page.screenshot(path='test_screenshots/drag_01_timeline_width.png')

            print("\n5️⃣ 드래그 리스너 초기화 상태 확인...")
            listener_state = page.evaluate("""
                () => {
                    return {
                        initialized: trimRangeState.dragListenersInitialized,
                        isDragging: trimRangeState.isDragging
                    };
                }
            """)
            print(f"✅ 드래그 리스너 초기화됨: {listener_state['initialized']}")
            print(f"✅ 현재 드래그 상태: {listener_state['isDragging']}")

            print("\n6️⃣ 시작 핸들 드래그 테스트...")
            start_handle = page.locator('#startHandle')
            container = page.locator('#timelineContainer')

            handle_box = start_handle.bounding_box()
            container_box = container.bounding_box()

            if handle_box and container_box:
                # 시작 위치
                start_x = handle_box['x'] + handle_box['width'] / 2
                start_y = handle_box['y'] + handle_box['height'] / 2

                # 목표 위치 (25% 지점)
                target_x = container_box['x'] + container_box['width'] * 0.25
                target_y = start_y

                print(f"   시작 위치: ({start_x:.0f}, {start_y:.0f})")
                print(f"   목표 위치: ({target_x:.0f}, {target_y:.0f})")

                # 드래그 전 상태
                before_state = page.evaluate("() => ({ startTime: trimRangeState.startTime, videoTime: videoPlayer.currentTime })")
                print(f"   드래그 전 - 시작 시간: {before_state['startTime']:.2f}초, 비디오 시간: {before_state['videoTime']:.2f}초")

                # 드래그 수행
                page.mouse.move(start_x, start_y)
                page.mouse.down()
                time.sleep(0.2)

                page.mouse.move(target_x, target_y)
                time.sleep(0.5)  # 비디오 seek가 일어날 시간

                # 드래그 중 상태
                during_state = page.evaluate("() => ({ startTime: trimRangeState.startTime, videoTime: videoPlayer.currentTime, isDragging: trimRangeState.isDragging })")
                print(f"   드래그 중 - 시작 시간: {during_state['startTime']:.2f}초, 비디오 시간: {during_state['videoTime']:.2f}초")
                print(f"   드래그 중 - isDragging: {during_state['isDragging']}")

                page.mouse.up()
                time.sleep(0.3)

                # 드래그 후 상태
                after_state = page.evaluate("() => ({ startTime: trimRangeState.startTime, videoTime: videoPlayer.currentTime, isDragging: trimRangeState.isDragging })")
                print(f"   드래그 후 - 시작 시간: {after_state['startTime']:.2f}초, 비디오 시간: {after_state['videoTime']:.2f}초")
                print(f"   드래그 후 - isDragging: {after_state['isDragging']}")

                if during_state['isDragging']:
                    print("✅ 드래그 상태가 정상적으로 감지됨")
                else:
                    print("❌ 드래그 상태가 감지되지 않음!")

                if abs(after_state['startTime'] - after_state['videoTime']) < 0.5:
                    print("✅ 비디오 seek가 정상 작동함")
                else:
                    print("⚠️ 비디오 seek 시간 차이가 있음")

                page.screenshot(path='test_screenshots/drag_02_after_drag.png')

            print("\n7️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n8️⃣ 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지 (최근 5개):")
                for msg in console_messages[-5:]:
                    print(f"  {msg}")

            print("\n" + "=" * 60)
            print("✅ 드래그 및 너비 테스트 완료!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - drag_01_timeline_width.png: 타임라인 너비 확인")
            print("  - drag_02_after_drag.png: 드래그 후 상태")

            print("\n⏳ 15초 후 브라우저 종료...")
            time.sleep(15)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='test_screenshots/drag_error.png')

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_drag_and_width()
