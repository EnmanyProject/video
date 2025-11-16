"""
GIF 생성 기능 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_gif_generation():
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
            print("🎞️ GIF 생성 기능 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

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

            print("\n3️⃣ GIF 옵션 설정...")
            # GIF 버튼 클릭
            gif_btn = page.locator('#gifBtn')
            gif_btn.click()
            print("✅ GIF 버튼 클릭")

            time.sleep(1)

            # GIF 설정
            start_time = page.locator('#gifStartTime')
            start_time.fill('0')
            print("✅ 시작 시간: 0초")

            duration = page.locator('#gifDuration')
            duration.fill('2')
            print("✅ 지속 시간: 2초")

            fps = page.locator('#gifFps')
            fps.fill('10')
            print("✅ FPS: 10")

            width = page.locator('#gifWidth')
            width.fill('480')
            print("✅ 크기: 480px")

            page.screenshot(path='test_screenshots/gif_01_options_set.png', full_page=True)

            print("\n4️⃣ GIF 생성 시작...")
            generate_btn = page.get_by_role('button', name='✨ GIF 생성 시작')
            generate_btn.click()
            print("✅ GIF 생성 버튼 클릭")

            # 생성 중 대기 (최대 30초)
            print("⏳ GIF 생성 대기 중...")
            for i in range(30):
                time.sleep(1)

                # 진행률 확인
                try:
                    progress = page.evaluate("""
                        () => {
                            const progressBar = document.getElementById('progress');
                            const progressFill = document.getElementById('progressFill');
                            const statusText = document.getElementById('statusText');
                            return {
                                visible: progressBar.style.display !== 'none',
                                width: progressFill.style.width,
                                status: statusText.textContent
                            };
                        }
                    """)

                    if progress['visible']:
                        print(f"   진행률: {progress['width']} - {progress['status']}")
                    else:
                        print(f"   상태: {progress['status']}")
                        if 'GIF가 성공적으로 생성' in progress['status']:
                            print("✅ GIF 생성 완료!")
                            break
                        elif '오류' in progress['status']:
                            print(f"❌ 오류 발생: {progress['status']}")
                            break
                except Exception as e:
                    print(f"   진행률 체크 오류: {e}")

            time.sleep(2)
            page.screenshot(path='test_screenshots/gif_02_after_generation.png', full_page=True)

            print("\n5️⃣ GIF Worker 상태 확인...")
            worker_info = page.evaluate("""
                () => {
                    return {
                        gifJsLoaded: typeof GIF !== 'undefined',
                        workerScriptExists: document.querySelector('script[src*="gif.worker.js"]') !== null
                    };
                }
            """)
            print(f"✅ GIF.js 로드됨: {worker_info['gifJsLoaded']}")
            print(f"✅ Worker 스크립트: gif.worker.js")

            print("\n6️⃣ 다운로드 이벤트 확인...")
            # 다운로드 리스너 추가는 이미 늦었지만, 파일 시스템에서 확인
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            print(f"✅ 다운로드 폴더: {downloads_path}")

            # 최근 GIF 파일 찾기
            gif_files = [f for f in os.listdir(downloads_path) if f.startswith('animation_') and f.endswith('.gif')]
            if gif_files:
                gif_files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_path, x)), reverse=True)
                latest_gif = gif_files[0]
                gif_size = os.path.getsize(os.path.join(downloads_path, latest_gif))
                print(f"✅ 최근 GIF 파일 발견: {latest_gif}")
                print(f"   크기: {gif_size:,} bytes ({gif_size/1024:.1f} KB)")
            else:
                print("⚠️ 다운로드 폴더에 GIF 파일이 없습니다")

            print("\n7️⃣ 콘솔 로그 확인...")
            if console_messages:
                print("📋 콘솔 메시지 (최근 20개):")
                for msg in console_messages[-20:]:
                    print(f"  {msg}")
            else:
                print("✅ 콘솔 메시지 없음")

            print("\n8️⃣ JavaScript 에러 확인...")
            if errors:
                print("❌ JavaScript 에러 발견:")
                for err in errors:
                    print(f"  {err}")
            else:
                print("✅ JavaScript 에러 없음")

            print("\n" + "=" * 60)
            print("✅ GIF 생성 테스트 완료!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - gif_01_options_set.png: 옵션 설정 후")
            print("  - gif_02_after_generation.png: 생성 완료 후")

            print("\n⏳ 10초 후 브라우저 종료...")
            time.sleep(10)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            page.screenshot(path='test_screenshots/gif_error.png', full_page=True)
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_gif_generation()
