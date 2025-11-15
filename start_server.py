#!/usr/bin/env python3
"""
비디오 편집기 로컬 서버 실행 스크립트
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 8000

def find_available_port(start_port=8000, max_attempts=10):
    """사용 가능한 포트 찾기"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as test_server:
                return port
        except OSError:
            continue
    return None

def main():
    # 스크립트가 있는 디렉토리로 이동
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("=" * 60)
    print("🎬 비디오 편집기 로컬 서버")
    print("=" * 60)

    # 사용 가능한 포트 찾기
    port = find_available_port(PORT)
    if port is None:
        print(f"❌ 오류: 포트 {PORT}부터 {PORT+9}까지 모두 사용 중입니다.")
        sys.exit(1)

    # HTTP 서버 설정
    Handler = http.server.SimpleHTTPRequestHandler

    # CORS 헤더 추가를 위한 커스텀 핸들러
    class CORSRequestHandler(Handler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            super().end_headers()

        def log_message(self, format, *args):
            # 요청 로그를 간단하게 표시
            if args[1] == '200':
                print(f"✓ {args[0]}")
            else:
                print(f"✗ {args[0]} - {args[1]}")

    try:
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            url = f"http://localhost:{port}/index.html"

            print(f"\n✅ 서버가 시작되었습니다!")
            print(f"📍 주소: {url}")
            print(f"\n🌐 브라우저를 자동으로 엽니다...")
            print(f"\n종료하려면 Ctrl+C를 누르세요.")
            print("=" * 60 + "\n")

            # 브라우저 자동 열기
            webbrowser.open(url)

            # 서버 실행
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 서버를 종료합니다...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
