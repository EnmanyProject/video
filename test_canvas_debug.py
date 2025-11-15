"""
Canvas 디버그 테스트 - 빨간 배경이 보이는지 확인
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_canvas_debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("=" * 60)
            print("🔍 Canvas 디버그 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            # 초기 스크린샷
            page.screenshot(path='test_screenshots/canvas_01_initial.png', full_page=True)
            print("📸 초기 화면 저장")

            print("\n2️⃣ 테스트 비디오 로드...")
            # URL로 비디오 로드 (CORS 문제 없는 샘플)
            url_input = page.locator('#urlInput')
            # 작은 테스트 비디오
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)
            print(f"✅ URL 입력: {test_url}")

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            print("✅ URL 로드 버튼 클릭")

            # 비디오 로드 대기
            time.sleep(5)

            page.screenshot(path='test_screenshots/canvas_02_after_upload.png', full_page=True)
            print("📸 비디오 로드 후 저장")

            print("\n3️⃣ 텍스트 입력...")
            text_input = page.locator('#captureText')
            text_input.fill('테스트 텍스트')
            print("✅ 텍스트 입력: 테스트 텍스트")

            time.sleep(1)
            page.screenshot(path='test_screenshots/canvas_03_text_entered.png', full_page=True)
            print("📸 텍스트 입력 후 저장")

            print("\n4️⃣ Canvas 요소 정보 확인...")
            canvas_info = page.evaluate("""
                () => {
                    const video = document.getElementById('videoPlayer');
                    const previewCanvas = document.getElementById('previewCanvas');
                    const videoRect = video.getBoundingClientRect();
                    const canvasRect = previewCanvas.getBoundingClientRect();
                    const computedStyle = window.getComputedStyle(previewCanvas);

                    return {
                        video: {
                            width: video.videoWidth,
                            height: video.videoHeight,
                            displayWidth: videoRect.width,
                            displayHeight: videoRect.height,
                            top: videoRect.top,
                            left: videoRect.left
                        },
                        canvas: {
                            width: previewCanvas.width,
                            height: previewCanvas.height,
                            displayWidth: canvasRect.width,
                            displayHeight: canvasRect.height,
                            top: canvasRect.top,
                            left: canvasRect.left,
                            zIndex: computedStyle.zIndex,
                            position: computedStyle.position,
                            display: computedStyle.display,
                            visibility: computedStyle.visibility,
                            opacity: computedStyle.opacity
                        }
                    };
                }
            """)

            print("✅ Video 정보:")
            print(f"   - 실제 크기: {canvas_info['video']['width']} x {canvas_info['video']['height']}")
            print(f"   - 표시 크기: {canvas_info['video']['displayWidth']} x {canvas_info['video']['displayHeight']}")
            print(f"   - 위치: top={canvas_info['video']['top']}, left={canvas_info['video']['left']}")

            print("\n✅ Canvas 정보:")
            print(f"   - 실제 크기: {canvas_info['canvas']['width']} x {canvas_info['canvas']['height']}")
            print(f"   - 표시 크기: {canvas_info['canvas']['displayWidth']} x {canvas_info['canvas']['displayHeight']}")
            print(f"   - 위치: top={canvas_info['canvas']['top']}, left={canvas_info['canvas']['left']}")
            print(f"   - z-index: {canvas_info['canvas']['zIndex']}")
            print(f"   - position: {canvas_info['canvas']['position']}")
            print(f"   - display: {canvas_info['canvas']['display']}")
            print(f"   - visibility: {canvas_info['canvas']['visibility']}")
            print(f"   - opacity: {canvas_info['canvas']['opacity']}")

            print("\n5️⃣ Canvas에 직접 그리기 테스트...")
            page.evaluate("""
                () => {
                    const canvas = document.getElementById('previewCanvas');
                    const ctx = canvas.getContext('2d');

                    // 빨간 사각형 그리기
                    ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 큰 텍스트 그리기
                    ctx.fillStyle = '#FFFF00';
                    ctx.font = 'bold 100px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('TEST', canvas.width / 2, canvas.height / 2);

                    console.log('Canvas에 직접 그리기 완료');
                }
            """)
            print("✅ Canvas에 빨간 배경 + 노란 텍스트 직접 그림")

            time.sleep(1)
            page.screenshot(path='test_screenshots/canvas_04_manual_draw.png', full_page=True)
            print("📸 수동 그리기 후 저장")

            print("\n6️⃣ 부모 요소 확인...")
            parent_info = page.evaluate("""
                () => {
                    const videoSection = document.querySelector('.video-section');
                    const rect = videoSection.getBoundingClientRect();
                    const style = window.getComputedStyle(videoSection);

                    return {
                        position: style.position,
                        display: style.display,
                        width: rect.width,
                        height: rect.height
                    };
                }
            """)
            print("✅ .video-section 정보:")
            print(f"   - position: {parent_info['position']}")
            print(f"   - display: {parent_info['display']}")
            print(f"   - 크기: {parent_info['width']} x {parent_info['height']}")

            print("\n" + "=" * 60)
            print("✅ 테스트 완료!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - canvas_01_initial.png")
            print("  - canvas_02_after_upload.png")
            print("  - canvas_03_text_entered.png")
            print("  - canvas_04_manual_draw.png (Canvas에 직접 그린 결과)")

            print("\n⏳ 10초 후 브라우저 종료...")
            time.sleep(10)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            page.screenshot(path='test_screenshots/canvas_error.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_canvas_debug()
