"""
드래그 기능 상세 디버깅
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_drag_debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 콘솔 로그 수집
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        try:
            print("=" * 60)
            print("🔍 드래그 기능 상세 디버깅")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속 및 비디오 로드...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')

            # 로컬 파일 선택기 사용 (URL은 CORS 문제로 인해 제한적)
            print("   로컬 파일을 선택해주세요...")

            # 파일 업로드 대신 디버깅 코드 추가
            page.evaluate("""
                () => {
                    // 드래그 이벤트 로깅 추가
                    console.log('=== 디버깅 코드 주입 ===');

                    window.dragDebugLog = [];

                    // 원본 addEventListener 저장
                    const originalAddEventListener = EventTarget.prototype.addEventListener;

                    // addEventListener 래핑
                    EventTarget.prototype.addEventListener = function(type, listener, options) {
                        if (['mousedown', 'mousemove', 'mouseup'].includes(type)) {
                            const targetInfo = this.id || this.className || this.tagName;
                            console.log(`[EventListener] ${type} 등록됨 on ${targetInfo}`);
                            window.dragDebugLog.push(`Registered ${type} on ${targetInfo}`);
                        }
                        return originalAddEventListener.call(this, type, listener, options);
                    };
                }
            """)

            print("✅ 디버깅 코드 주입 완료")

            # URL 로드로 테스트
            url_input = page.locator('#urlInput')
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            print("✅ 비디오 로드 중...")

            time.sleep(3)

            print("\n2️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn = page.locator('#trimBtn')
            trim_btn.click()
            time.sleep(1)

            print("\n3️⃣ 이벤트 리스너 등록 확인...")
            debug_log = page.evaluate("() => window.dragDebugLog || []")
            if debug_log:
                print("📋 등록된 이벤트 리스너:")
                for log in debug_log[-10:]:
                    print(f"   {log}")
            else:
                print("⚠️ 이벤트 리스너 로그 없음")

            print("\n4️⃣ 핸들 요소 상태 확인...")
            handle_info = page.evaluate("""
                () => {
                    const startHandle = document.getElementById('startHandle');
                    const endHandle = document.getElementById('endHandle');
                    const container = document.getElementById('timelineContainer');

                    const getElementInfo = (el, name) => {
                        if (!el) return { name, exists: false };

                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);

                        return {
                            name,
                            exists: true,
                            visible: style.display !== 'none' && style.visibility !== 'hidden',
                            rect: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            },
                            zIndex: style.zIndex,
                            cursor: style.cursor,
                            pointerEvents: style.pointerEvents
                        };
                    };

                    return {
                        startHandle: getElementInfo(startHandle, 'startHandle'),
                        endHandle: getElementInfo(endHandle, 'endHandle'),
                        container: getElementInfo(container, 'container')
                    };
                }
            """)

            for name, info in handle_info.items():
                print(f"\n   {info['name']}:")
                if info['exists']:
                    print(f"      - Visible: {info['visible']}")
                    print(f"      - Position: ({info['rect']['x']:.0f}, {info['rect']['y']:.0f})")
                    print(f"      - Size: {info['rect']['width']:.0f}x{info['rect']['height']:.0f}")
                    print(f"      - z-index: {info['zIndex']}")
                    print(f"      - cursor: {info['cursor']}")
                    print(f"      - pointer-events: {info['pointerEvents']}")
                else:
                    print(f"      ❌ 존재하지 않음")

            print("\n5️⃣ 시작 핸들 수동 클릭 시도...")
            start_handle = page.locator('#startHandle')

            # 핸들의 중앙 위치 계산
            box = start_handle.bounding_box()
            if box:
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2

                print(f"   핸들 중앙 위치: ({center_x:.0f}, {center_y:.0f})")

                # 클릭 전 상태
                before_click = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, dragTarget: trimRangeState.dragTarget })")
                print(f"   클릭 전: isDragging={before_click['isDragging']}, dragTarget={before_click['dragTarget']}")

                # 마우스 이동
                page.mouse.move(center_x, center_y)
                time.sleep(0.3)

                # 마우스 다운
                print("   마우스 다운...")
                page.mouse.down()
                time.sleep(0.3)

                # 클릭 후 상태
                after_click = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, dragTarget: trimRangeState.dragTarget })")
                print(f"   마우스 다운 후: isDragging={after_click['isDragging']}, dragTarget={after_click['dragTarget']}")

                if after_click['isDragging']:
                    print("   ✅ 드래그 상태가 True로 변경됨!")
                else:
                    print("   ❌ 드래그 상태가 변경되지 않음!")

                # 마우스 이동 테스트
                print("\n   마우스 이동 테스트...")
                new_x = center_x + 100
                page.mouse.move(new_x, center_y)
                time.sleep(0.3)

                # 이동 후 상태
                after_move = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, startTime: trimRangeState.startTime })")
                print(f"   이동 후: isDragging={after_move['isDragging']}, startTime={after_move['startTime']:.2f}초")

                # 마우스 업
                page.mouse.up()
                time.sleep(0.3)

                final_state = page.evaluate("() => ({ isDragging: trimRangeState.isDragging, dragTarget: trimRangeState.dragTarget })")
                print(f"   마우스 업 후: isDragging={final_state['isDragging']}, dragTarget={final_state['dragTarget']}")

            print("\n6️⃣ 콘솔 메시지 확인...")
            if console_messages:
                print("📋 최근 콘솔 메시지:")
                for msg in console_messages[-15:]:
                    print(f"   {msg}")

            page.screenshot(path='test_screenshots/drag_debug.png')
            print("\n📸 스크린샷 저장: drag_debug.png")

            print("\n⏳ 20초 후 브라우저 종료...")
            time.sleep(20)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_drag_debug()
