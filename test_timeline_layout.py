"""
타임라인 레이아웃 확인 테스트
"""
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_timeline_layout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("=" * 60)
            print("📐 타임라인 레이아웃 확인 테스트")
            print("=" * 60)

            print("\n1️⃣ 페이지 접속...")
            page.goto('http://localhost:8000')
            page.wait_for_load_state('networkidle')
            print("✅ 페이지 로드 완료")

            page.screenshot(path='test_screenshots/layout_01_initial.png')

            print("\n2️⃣ 테스트 비디오 로드...")
            url_input = page.locator('#urlInput')
            test_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            url_input.fill(test_url)

            load_btn = page.get_by_text('URL에서 불러오기')
            load_btn.click()
            print("✅ URL 로드 버튼 클릭")

            time.sleep(3)
            page.screenshot(path='test_screenshots/layout_02_video_loaded.png')

            print("\n3️⃣ 구간 잘라내기 버튼 클릭...")
            trim_btn = page.locator('#trimBtn')
            trim_btn.click()
            print("✅ 버튼 클릭됨")

            time.sleep(1)
            page.screenshot(path='test_screenshots/layout_03_timeline_visible.png')

            print("\n4️⃣ 레이아웃 정보 확인...")
            layout_info = page.evaluate("""
                () => {
                    const videoSection = document.querySelector('.video-section');
                    const videoPlayer = document.getElementById('videoPlayer');
                    const timeline = document.getElementById('timelineRangeSelector');
                    const controls = document.querySelector('.controls');

                    const getInfo = (el, name) => {
                        if (!el) return { name, exists: false };
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return {
                            name,
                            exists: true,
                            top: rect.top,
                            left: rect.left,
                            width: rect.width,
                            height: rect.height,
                            display: style.display,
                            position: style.position
                        };
                    };

                    return {
                        videoSection: getInfo(videoSection, 'video-section'),
                        videoPlayer: getInfo(videoPlayer, 'videoPlayer'),
                        timeline: getInfo(timeline, 'timelineRangeSelector'),
                        controls: getInfo(controls, 'controls')
                    };
                }
            """)

            print("\n📊 레이아웃 정보:")
            for key, info in layout_info.items():
                print(f"\n{info['name']}:")
                if info['exists']:
                    print(f"  - 위치: top={info['top']:.1f}, left={info['left']:.1f}")
                    print(f"  - 크기: width={info['width']:.1f}, height={info['height']:.1f}")
                    print(f"  - display: {info['display']}, position: {info['position']}")
                else:
                    print(f"  - 존재하지 않음")

            # 타임라인이 비디오 섹션 내부에 있는지 확인
            if layout_info['timeline']['exists'] and layout_info['videoSection']['exists']:
                timeline_top = layout_info['timeline']['top']
                video_bottom = layout_info['videoSection']['top'] + layout_info['videoSection']['height']
                video_top = layout_info['videoSection']['top']

                print(f"\n🔍 위치 관계 분석:")
                print(f"  - 비디오 섹션 범위: top={video_top:.1f} ~ bottom={video_bottom:.1f}")
                print(f"  - 타임라인 시작 위치: top={timeline_top:.1f}")

                if video_top <= timeline_top <= video_bottom:
                    print(f"  ✅ 타임라인이 비디오 섹션 내부에 있습니다")
                else:
                    print(f"  ❌ 타임라인이 비디오 섹션 밖에 있습니다!")

            print("\n5️⃣ HTML 구조 확인...")
            structure = page.evaluate("""
                () => {
                    const videoSection = document.querySelector('.video-section');
                    const children = Array.from(videoSection.children).map(child => ({
                        tag: child.tagName,
                        id: child.id,
                        class: child.className,
                        display: window.getComputedStyle(child).display
                    }));
                    return children;
                }
            """)

            print("\n📋 video-section 내부 구조:")
            for i, child in enumerate(structure):
                print(f"  {i+1}. <{child['tag']}> id='{child['id']}' class='{child['class']}' display={child['display']}")

            print("\n" + "=" * 60)
            print("✅ 레이아웃 확인 완료!")
            print("=" * 60)
            print("\n📁 스크린샷:")
            print("  - layout_01_initial.png: 초기 화면")
            print("  - layout_02_video_loaded.png: 비디오 로드 후")
            print("  - layout_03_timeline_visible.png: 타임라인 표시")

            print("\n⏳ 15초 후 브라우저 종료... (스크린샷을 확인하세요)")
            time.sleep(15)

        except Exception as e:
            print(f"\n❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='test_screenshots/layout_error.png')
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    os.makedirs('test_screenshots', exist_ok=True)
    test_timeline_layout()
