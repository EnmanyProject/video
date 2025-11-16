"""
실제 브라우저에서 드래그 이벤트 확인 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_real_drag():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 콘솔 로그 수집
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        try:
            print("=" * 60)
            print("🔍 실제 드래그 이벤트 확인")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')

            # 드래그 이벤트 로깅 코드 주입
            print("\n2️⃣ 이벤트 로깅 코드 주입...")
            page.evaluate("""
                () => {
                    window.dragEvents = [];

                    // 모든 마우스 이벤트 로깅
                    ['mousedown', 'mousemove', 'mouseup', 'click'].forEach(eventType => {
                        document.addEventListener(eventType, (e) => {
                            const target = e.target.id || e.target.className || e.target.tagName;
                            const log = `${eventType} on ${target} at (${e.clientX}, ${e.clientY})`;
                            window.dragEvents.push(log);
                            console.log(`[Event] ${log}`);
                        }, true);
                    });

                    console.log('✅ 이벤트 로깅 활성화');
                }
            """)

            print("\n3️⃣ 비디오 로드...")
            url_input = page.locator('#urlInput')
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            time.sleep(4)

            print("\n4️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn = page.locator('#trimBtn')
            trim_btn.click()
            time.sleep(1)

            # 핸들 정보 확인
            print("\n5️⃣ 핸들 상태 확인...")
            handle_info = page.evaluate("""
                () => {
                    const startHandle = document.getElementById('startHandle');
                    const endHandle = document.getElementById('endHandle');

                    if (!startHandle || !endHandle) {
                        return { error: '핸들 요소를 찾을 수 없습니다' };
                    }

                    const startRect = startHandle.getBoundingClientRect();
                    const endRect = endHandle.getBoundingClientRect();

                    return {
                        startHandle: {
                            rect: { x: startRect.x, y: startRect.y, width: startRect.width, height: startRect.height },
                            visible: startHandle.offsetParent !== null,
                            style: window.getComputedStyle(startHandle).pointerEvents
                        },
                        endHandle: {
                            rect: { x: endRect.x, y: endRect.y, width: endRect.width, height: endRect.height },
                            visible: endHandle.offsetParent !== null,
                            style: window.getComputedStyle(endHandle).pointerEvents
                        },
                        dragListenersInitialized: trimRangeState.dragListenersInitialized
                    };
                }
            """)

            if 'error' in handle_info:
                print(f"❌ {handle_info['error']}")
                return

            print(f"✅ 시작 핸들: 위치=({handle_info['startHandle']['rect']['x']:.0f}, {handle_info['startHandle']['rect']['y']:.0f}), "
                  f"크기={handle_info['startHandle']['rect']['width']:.0f}x{handle_info['startHandle']['rect']['height']:.0f}")
            print(f"✅ 종료 핸들: 위치=({handle_info['endHandle']['rect']['x']:.0f}, {handle_info['endHandle']['rect']['y']:.0f}), "
                  f"크기={handle_info['endHandle']['rect']['width']:.0f}x{handle_info['endHandle']['rect']['height']:.0f}")
            print(f"✅ 드래그 리스너 초기화됨: {handle_info['dragListenersInitialized']}")

            # 이벤트 카운터 리셋
            page.evaluate("window.dragEvents = []")

            print("\n6️⃣ 시작 핸들 실제 드래그 테스트...")
            start_handle = page.locator('#startHandle')

            # 핸들 위에서 클릭 및 드래그
            box = start_handle.bounding_box()
            if box:
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2
                target_x = center_x + 150

                print(f"   시작 위치: ({center_x:.0f}, {center_y:.0f})")
                print(f"   목표 위치: ({target_x:.0f}, {center_y:.0f})")

                # 상태 확인
                before = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, startTime: trimRangeState.startTime })")
                print(f"   드래그 전: isDragging={before['isDragging']}, startTime={before['startTime']:.2f}초")

                # 실제 드래그 수행
                page.mouse.move(center_x, center_y)
                time.sleep(0.2)

                page.mouse.down()
                time.sleep(0.3)

                during = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, dragTarget: trimRangeState.dragTarget })")
                print(f"   마우스 다운 후: isDragging={during['isDragging']}, dragTarget={during['dragTarget']}")

                # 이동
                page.mouse.move(target_x, center_y, steps=10)
                time.sleep(0.5)

                moving = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, startTime: trimRangeState.startTime })")
                print(f"   이동 중: isDragging={moving['isDragging']}, startTime={moving['startTime']:.2f}초")

                page.mouse.up()
                time.sleep(0.3)

                after = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, startTime: trimRangeState.startTime })")
                print(f"   드래그 후: isDragging={after['isDragging']}, startTime={after['startTime']:.2f}초")

                # 시간이 변경되었는지 확인
                if abs(after['startTime'] - before['startTime']) > 0.1:
                    print(f"   ✅ 시작 시간 변경됨: {before['startTime']:.2f}초 → {after['startTime']:.2f}초")
                else:
                    print(f"   ❌ 시작 시간이 변경되지 않음!")

            # 발생한 이벤트 확인
            print("\n7️⃣ 발생한 이벤트 확인...")
            events = page.evaluate("() => window.dragEvents || []")
            if events:
                print(f"✅ 총 {len(events)}개 이벤트 발생:")
                for event in events[-10:]:
                    print(f"   {event}")
            else:
                print("❌ 이벤트가 전혀 발생하지 않음!")

            print("\n8️⃣ 콘솔 메시지 확인...")
            if console_messages:
                print("📋 최근 콘솔 메시지:")
                for msg in console_messages[-15:]:
                    print(f"   {msg}")

            print("\n✅ 테스트 완료!")
            print("\n⏳ 브라우저를 수동으로 테스트해보세요...")
            print("   핸들을 마우스로 드래그해보고 움직이는지 확인하세요!")
            time.sleep(30)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()

if __name__ == "__main__":
    test_real_drag()
