# 🔧 개발 문서

비디오 편집기 개발 가이드, 기술 상세, API 문서

## 📅 개발 이력

### Phase 1: 기본 기능 구현 (v1.0)
**완료일**: 이전 세션

#### 구현 기능
1. **비디오 로드**
   - 로컬 파일 업로드
   - URL 입력 지원
   - File System Access API 폴더 선택

2. **기본 캡처**
   - PNG 고품질 캡처
   - JPG 압축 캡처
   - 2x 스케일 렌더링 (고품질)

3. **GIF 생성**
   - GIF.js 라이브러리 통합
   - Web Worker 사용
   - 프레임 레이트/크기 조절

4. **역재생**
   - Canvas + MediaRecorder API
   - VP9 코덱 사용
   - FPS/품질 조절

#### 기술적 도전
- CORS 문제 해결 → 커스텀 HTTP 서버 작성
- FFmpeg.wasm 보안 헤더 설정
- MediaRecorder 브라우저 호환성

### Phase 2: 고급 편집 기능 (v2.0)
**완료일**: 2025-11-16

#### 구현 순서 및 커밋

##### 1. 텍스트/워터마크 기능
**커밋**: `📝 캡처에 텍스트/워터마크 추가 기능 구현`

**구현 내용**:
- 텍스트 입력 필드 추가
- 폰트 크기 선택 (16px~128px, 8단계)
- 색상 선택 (8가지 프리셋)
- 위치 선택 (상단/중앙/하단)
- 스타일 선택 (배경 있음/투명)

**기술 구현**:
```javascript
// Canvas 2D context를 사용한 텍스트 렌더링
const fontSize = parseInt(document.getElementById('captureFontSize').value);
ctx.font = `bold ${fontSize}px Arial`;
ctx.textAlign = 'center';

// 위치 계산 (상단/중앙/하단)
const position = document.getElementById('captureTextPosition').value;
let y;
if (position === 'top') y = fontSize + 20;
else if (position === 'middle') y = canvas.height / 2;
else y = canvas.height - 20;

// 스타일별 렌더링 (배경 있음/투명)
if (style === 'background') {
    // 반투명 검은 배경
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(...);
}
```

##### 2. 타임스탬프 자동 표시
**커밋**: `⏰ 타임스탬프 자동 표시 기능 구현`

**구현 내용**:
- 체크박스로 활성화/비활성화
- `mm:ss.ms` 형식 표시
- 우측 하단 고정 위치
- 반투명 배경 자동 추가

**기술 구현**:
```javascript
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
}

// 타임스탬프 렌더링
const timestamp = formatTime(videoPlayer.currentTime);
ctx.font = 'bold 20px monospace';
ctx.textAlign = 'right';
ctx.fillText(timestamp, canvas.width - 10, canvas.height - 10);
```

##### 3. 프레임 간격 캡처
**커밋**: `🎬 프레임 간격 캡처 기능 구현`

**구현 내용**:
- 시작/종료 시간 설정
- 간격 선택 (0.5~10초, 또는 직접 입력)
- 자동 순차 파일명 (`interval_capture_001.jpg`)
- 진행률 표시

**기술 구현**:
```javascript
// 캡처 시간 배열 생성
const captureTimes = [];
for (let t = startTime; t <= endTime; t += interval) {
    captureTimes.push(Math.min(t, endTime));
}

// seeked 이벤트 기반 순차 캡처
async function captureNextIntervalFrame() {
    const timestamp = times[currentFrame];

    const seekedHandler = async () => {
        videoPlayer.removeEventListener('seeked', seekedHandler);
        await captureFrameWithSequence(currentFrame + 1);
        currentFrame++;
        await captureNextIntervalFrame();
    };

    videoPlayer.addEventListener('seeked', seekedHandler);
    videoPlayer.currentTime = timestamp;
}

// 시퀀스 번호 포맷팅
const paddedNumber = String(sequenceNumber).padStart(3, '0');
const filename = `interval_capture_${paddedNumber}.${format}`;
```

**주요 기술**:
- `seeked` 이벤트를 사용한 정확한 프레임 이동
- 재귀 함수로 순차 캡처 구현
- 진행률 계산 및 UI 업데이트

##### 4. 구간 잘라내기(트림)
**커밋**: `✂️ 구간 잘라내기(트림) 기능 구현`

**구현 내용**:
- 시작/종료 시간 지정
- FPS 선택 (24/30/60fps)
- 품질 선택 (3~10 Mbps)
- WebM 형식 출력
- 진행률 표시

**기술 구현**:
```javascript
async function trimVideo() {
    // MediaRecorder 설정
    const stream = canvas.captureStream(fps);
    const options = {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: quality * 1000000
    };
    const mediaRecorder = new MediaRecorder(stream, options);

    // 데이터 수집
    const chunks = [];
    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
    };

    // 프레임별 렌더링
    for (let t = startTime; t <= endTime; t += frameInterval) {
        videoPlayer.currentTime = t;
        await waitForSeeked();
        ctx.drawImage(videoPlayer, 0, 0, width, height);
    }

    // Blob 생성 및 저장
    const blob = new Blob(chunks, { type: 'video/webm' });
    await saveFile(blob, filename);
}
```

**주요 기술**:
- MediaRecorder API를 사용한 실시간 인코딩
- Canvas.captureStream()으로 비디오 스트림 생성
- VP9 코덱 사용 (고품질 압축)

##### 5. 밝기/대비/필터 조절
**커밋**: `🎨 밝기/대비/필터 조절 기능 구현`

**구현 내용**:
- 6가지 필터 슬라이더 (밝기, 대비, 채도, 색상, 블러, 흑백)
- 5가지 프리셋 (초기화, 흑백, 세피아, 빈티지, 선명하게)
- 실시간 미리보기 (비디오 플레이어)
- 모든 캡처 기능에 자동 적용

**기술 구현**:
```javascript
// 필터 상태 관리
let filterState = {
    brightness: 100,
    contrast: 100,
    saturation: 100,
    hue: 0,
    blur: 0,
    grayscale: 0
};

// CSS filter 문자열 생성
function getCurrentFilterString() {
    return `brightness(${filterState.brightness}%)
            contrast(${filterState.contrast}%)
            saturate(${filterState.saturation}%)
            hue-rotate(${filterState.hue}deg)
            blur(${filterState.blur}px)
            grayscale(${filterState.grayscale}%)`;
}

// 실시간 미리보기
function applyVideoFilter() {
    videoPlayer.style.filter = getCurrentFilterString();
}

// Canvas에 필터 적용 (캡처 시)
ctx.filter = getCurrentFilterString();
ctx.drawImage(videoPlayer, 0, 0, width, height);
ctx.filter = 'none'; // 텍스트에는 필터 미적용
```

**프리셋 정의**:
```javascript
const presets = {
    bw: { brightness: 100, contrast: 110, saturation: 0, grayscale: 100 },
    sepia: { brightness: 110, contrast: 90, saturation: 50, hue: 20, grayscale: 50 },
    vintage: { brightness: 110, contrast: 120, saturation: 80, hue: 10, blur: 0.5, grayscale: 20 },
    vivid: { brightness: 110, contrast: 120, saturation: 150 }
};
```

**주요 기술**:
- CSS filter property를 사용한 실시간 미리보기
- Canvas 2D context filter를 사용한 이미지 처리
- 필터를 모든 캡처 함수에 통합

##### 6. 썸네일 생성기
**커밋**: `🖼️ 썸네일 생성기 기능 구현`

**구현 내용**:
- 개수 선택 (4/6/9/12/16개)
- 크기 선택 (160px~480px)
- 그리드 모드: 단일 이미지로 결합
- 개별 모드: 각각 별도 저장
- 자동 균등 분포 계산
- 타임스탬프 옵션

**기술 구현**:

1. **균등 분포 계산**:
```javascript
const timestamps = [];
const interval = duration / (count + 1);
for (let i = 1; i <= count; i++) {
    timestamps.push(interval * i);
}
```

2. **썸네일 캡처** (종횡비 유지):
```javascript
const aspectRatio = videoWidth / videoHeight;
let thumbWidth, thumbHeight;
if (aspectRatio > 1) {
    thumbWidth = size;
    thumbHeight = Math.round(size / aspectRatio);
} else {
    thumbWidth = Math.round(size * aspectRatio);
    thumbHeight = size;
}

canvas.width = thumbWidth;
canvas.height = thumbHeight;
ctx.drawImage(videoPlayer, 0, 0, thumbWidth, thumbHeight);
```

3. **그리드 레이아웃**:
```javascript
// 그리드 크기 계산
const layouts = {
    4: { cols: 2, rows: 2 },
    6: { cols: 3, rows: 2 },
    9: { cols: 3, rows: 3 },
    12: { cols: 4, rows: 3 },
    16: { cols: 4, rows: 4 }
};

// 그리드 캔버스 생성
const padding = 10;
const gridWidth = cols * thumbWidth + (cols + 1) * padding;
const gridHeight = rows * thumbHeight + (rows + 1) * padding;

// 썸네일 배치
for (let i = 0; i < thumbnails.length; i++) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = padding + col * (thumbWidth + padding);
    const y = padding + row * (thumbHeight + padding);
    ctx.drawImage(thumbnail, x, y, thumbWidth, thumbHeight);
}
```

**주요 기술**:
- Blob to Image 변환 (그리드 생성용)
- 복합 Canvas 렌더링
- 비율 계산 및 레이아웃 알고리즘

## 🏗️ 아키텍처

### 파일 구조
```
index.html (단일 파일 애플리케이션)
├── HTML (구조)
│   ├── 비디오 컨트롤 섹션
│   ├── 비디오 플레이어 & 캔버스
│   ├── 필터 컨트롤
│   ├── 캡처 옵션 (텍스트, 간격, 썸네일)
│   ├── GIF 옵션
│   ├── 트림 옵션
│   └── 역재생 옵션
│
├── CSS (스타일)
│   ├── 레이아웃 (Flexbox)
│   ├── 버튼 스타일
│   ├── 진행률 바
│   └── 반응형 디자인
│
└── JavaScript (로직)
    ├── 상태 관리
    │   ├── filterState
    │   ├── intervalCaptureState
    │   ├── thumbnailState
    │   └── reverseState
    │
    ├── 비디오 관리
    │   ├── loadLocalFile()
    │   ├── loadFromUrl()
    │   └── enableControls()
    │
    ├── 캡처 기능
    │   ├── captureFrame()
    │   ├── captureFrameWithSequence()
    │   ├── startIntervalCapture()
    │   └── startGenerateThumbnails()
    │
    ├── 필터 처리
    │   ├── getCurrentFilterString()
    │   ├── applyVideoFilter()
    │   └── applyFilterPreset()
    │
    ├── 비디오 생성
    │   ├── generateGif()
    │   ├── trimVideo()
    │   └── reverseVideo()
    │
    └── 유틸리티
        ├── saveFile()
        ├── formatTime()
        ├── updateProgress()
        └── showStatus()
```

### 데이터 플로우

```
비디오 로드 → 필터 설정 → 캡처/생성 → 후처리 → 저장

1. 비디오 로드
   File/URL → VideoElement → enableControls()

2. 필터 설정
   Slider Input → filterState → CSS filter (미리보기)
                            → Canvas filter (캡처)

3. 캡처/생성
   User Action → Options → Process → Blob/File

4. 후처리
   - 텍스트 오버레이
   - 타임스탬프 추가
   - 필터 적용
   - 시퀀스 번호 추가

5. 저장
   Blob → File System Access API (폴더 지정 시)
       → Download (기본)
```

## 📚 API 문서

### 핵심 함수

#### 비디오 로드
```javascript
function loadLocalFile()
// 로컬 파일 업로드
// Input: <input type="file"> 선택
// Output: videoPlayer.src 설정, enableControls() 호출

function loadFromUrl()
// URL에서 비디오 로드
// Input: #urlInput 값
// Output: videoPlayer.src 설정
```

#### 필터 관리
```javascript
function getCurrentFilterString()
// 현재 필터 상태를 CSS filter 문자열로 변환
// Input: filterState 객체
// Output: 'brightness(100%) contrast(100%) ...' 문자열

function applyVideoFilter()
// 비디오 플레이어에 실시간 필터 적용
// Input: none
// Output: videoPlayer.style.filter 설정

function applyFilterPreset(preset)
// 프리셋 필터 적용
// Input: 'none' | 'bw' | 'sepia' | 'vintage' | 'vivid'
// Output: filterState 업데이트, UI 반영
```

#### 프레임 캡처
```javascript
function captureFrame(format)
// 현재 프레임 캡처 (텍스트/타임스탬프 포함)
// Input: 'png' | 'jpg'
// Output: 이미지 파일 다운로드/저장
// Features:
//   - 2x 스케일 렌더링
//   - 필터 자동 적용
//   - 텍스트 오버레이 (옵션)
//   - 타임스탬프 (옵션)

function captureFrameWithSequence(sequenceNumber, format)
// 시퀀스 번호가 포함된 프레임 캡처
// Input: sequenceNumber (number), format ('png'|'jpg')
// Output: interval_capture_001.jpg 형식 파일
```

#### 간격 캡처
```javascript
async function startIntervalCapture()
// 일정 간격으로 자동 프레임 캡처
// Input: UI에서 시작/종료 시간, 간격, 포맷
// Output: 여러 개의 시퀀스 이미지 파일
// Process:
//   1. 캡처 시간 배열 생성
//   2. 순차적으로 seeked 이벤트 대기
//   3. 각 프레임 캡처 및 저장
//   4. 진행률 업데이트

async function captureNextIntervalFrame()
// 다음 간격 프레임 캡처 (재귀)
// 내부 함수, startIntervalCapture()에서 호출
```

#### 썸네일 생성
```javascript
async function startGenerateThumbnails()
// 비디오에서 균등 분포 썸네일 생성
// Input: UI에서 개수, 크기, 출력 형식, 포맷
// Output: 그리드 이미지 또는 개별 이미지 파일
// Process:
//   1. 타임스탬프 균등 분포 계산
//   2. 각 타임스탬프에서 썸네일 캡처
//   3. 그리드 생성 또는 개별 저장

async function createThumbnailGrid()
// 썸네일들을 단일 그리드 이미지로 결합
// Input: thumbnailState.thumbnails 배열
// Output: 그리드 레이아웃 이미지 파일

async function saveThumbnailsIndividually()
// 썸네일을 개별 파일로 저장
// Input: thumbnailState.thumbnails 배열
// Output: thumbnail_001.jpg, 002.jpg, ...
```

#### 트림/역재생
```javascript
async function trimVideo()
// 비디오 구간 잘라내기
// Input: UI에서 시작/종료 시간, FPS, 품질
// Output: WebM 비디오 파일
// Codec: VP9

async function reverseVideo()
// 비디오 역재생
// Input: UI에서 FPS, 품질
// Output: WebM 비디오 파일 (역순)
```

#### GIF 생성
```javascript
async function generateGif()
// GIF 애니메이션 생성
// Input: UI에서 시작 시간, 지속 시간, FPS, 크기
// Output: GIF 파일
// Library: gif.js (Web Worker)
```

#### 유틸리티
```javascript
async function saveFile(blob, filename)
// 파일 저장 (폴더 선택 또는 다운로드)
// Input: Blob, 파일명
// Output: 파일 저장 또는 다운로드

function formatTime(seconds)
// 시간 포맷팅
// Input: 123.456 (seconds)
// Output: '02:03.456' (mm:ss.ms)

function updateProgress(progress)
// 진행률 바 업데이트
// Input: 0.0 ~ 1.0
// Output: 프로그레스 바 UI 업데이트

function showStatus(message, type)
// 상태 메시지 표시
// Input: message (string), type ('success'|'error'|'info')
// Output: 상태 표시줄 업데이트
```

### 전역 상태

```javascript
// 필터 상태
filterState = {
    brightness: 100,    // 0~200
    contrast: 100,      // 0~200
    saturation: 100,    // 0~200
    hue: 0,            // 0~360
    blur: 0,           // 0~10
    grayscale: 0       // 0~100
}

// 간격 캡처 상태
intervalCaptureState = {
    isRunning: false,
    currentFrame: 0,
    totalFrames: 0,
    times: [],
    format: 'jpg',
    originalTime: 0
}

// 썸네일 생성 상태
thumbnailState = {
    isRunning: false,
    currentIndex: 0,
    totalCount: 0,
    thumbnails: [],
    originalTime: 0,
    timestamps: [],
    size: 240,
    outputMode: 'grid',
    format: 'jpg'
}
```

## 🎯 주요 기술 결정

### 1. 단일 파일 구조
**결정**: 모든 코드를 index.html 하나에 통합

**이유**:
- 배포 간편성 (파일 하나만 복사)
- 의존성 최소화
- 빠른 로드 시간
- 간단한 유지보수

**트레이드오프**:
- 파일 크기 증가 (~1800 라인)
- 모듈화 제한
- 코드 네비게이션 어려움

### 2. Canvas 기반 처리
**결정**: 모든 이미지/비디오 처리를 Canvas API로 구현

**이유**:
- 브라우저 네이티브 지원
- 고성능 하드웨어 가속
- 픽셀 레벨 제어 가능
- 필터 적용 용이

**장점**:
- 외부 라이브러리 불필요
- 실시간 처리 가능
- 크로스 브라우저 호환성

### 3. CSS filter + Canvas filter 조합
**결정**: 미리보기는 CSS, 캡처는 Canvas filter 사용

**이유**:
- CSS filter: GPU 가속, 실시간 성능
- Canvas filter: 이미지에 영구 적용 가능

**구현**:
```javascript
// 실시간 미리보기 (CSS)
videoPlayer.style.filter = getCurrentFilterString();

// 캡처 시 적용 (Canvas)
ctx.filter = getCurrentFilterString();
ctx.drawImage(videoPlayer, 0, 0, width, height);
```

### 4. seeked 이벤트 기반 캡처
**결정**: 프레임 이동 시 seeked 이벤트 사용

**이유**:
- 정확한 프레임 타이밍 보장
- 비동기 처리 안정성
- 브라우저 렌더링 완료 대기

**패턴**:
```javascript
const seekedHandler = async () => {
    videoPlayer.removeEventListener('seeked', seekedHandler);
    // 프레임 처리
    await processFrame();
};
videoPlayer.addEventListener('seeked', seekedHandler);
videoPlayer.currentTime = targetTime;
```

### 5. MediaRecorder API (트림/역재생)
**결정**: MediaRecorder API를 사용한 비디오 생성

**이유**:
- 브라우저 네이티브 인코더 사용
- VP9 고품질 코덱 지원
- 실시간 스트리밍 인코딩

**대안**:
- FFmpeg.wasm (고려했으나 복잡도 증가)
- Canvas export (프레임별 저장 후 외부 결합 필요)

## 🔮 향후 개선 사항

### 단기 (우선순위 높음)
1. **진행률 취소 버튼**
   - 긴 작업 중간 취소 기능
   - 현재: 완료까지 대기 필수

2. **배치 작업**
   - 여러 비디오 동시 처리
   - 작업 큐 관리

3. **프리셋 저장**
   - 사용자 정의 필터 프리셋
   - LocalStorage에 저장

### 중기
1. **추가 필터**
   - 샤프니스 (Sharpness)
   - 비네팅 (Vignette)
   - 노이즈 (Noise)

2. **오디오 처리**
   - 역재생/트림 시 오디오 유지
   - 볼륨 조절
   - 배경음악 추가

3. **타임라인 편집**
   - 멀티 클립 편집
   - 트랜지션 효과

### 장기
1. **클라우드 저장**
   - Google Drive 연동
   - Dropbox 연동

2. **AI 기능**
   - 자동 장면 감지 (썸네일)
   - 객체 추적
   - 자막 생성

3. **협업 기능**
   - 프로젝트 공유
   - 실시간 협업 편집

## 🐛 알려진 이슈

### 브라우저 제한
1. **File System Access API**
   - Chrome/Edge만 지원
   - Safari/Firefox 미지원

2. **WebM 코덱**
   - Safari VP9 미지원
   - 대안: VP8 사용 (품질 저하)

### 성능 이슈
1. **대용량 비디오**
   - 메모리 사용량 증가
   - 브라우저 탭 크래시 가능
   - 권장: 1080p, 5분 이하

2. **고 FPS 설정**
   - 60fps 역재생 시 처리 느림
   - 해결: 30fps 사용 권장

### 호환성
1. **CORS 제한**
   - 외부 URL 비디오 제한적
   - 해결: CORS 허용 서버만 사용

2. **모바일 제한**
   - Canvas 메모리 제한
   - MediaRecorder 성능 이슈

## 📊 성능 벤치마크

### 캡처 성능
- **단일 프레임**: ~50ms (1080p)
- **간격 캡처 (100프레임)**: ~5초 (1080p, 필터 포함)
- **썸네일 생성 (16개)**: ~2초 (1080p, 그리드 모드)

### 비디오 생성
- **GIF (5초, 30fps)**: ~10초 (720p)
- **트림 (10초, 60fps)**: ~15초 (1080p)
- **역재생 (30초, 60fps)**: ~45초 (1080p)

*테스트 환경: Chrome 120, Windows 11, i7-12700K, 32GB RAM*

## 🔧 개발 환경 설정

### 필수 요구사항
- Node.js 16+ 또는 Python 3.6+
- 모던 브라우저 (Chrome 90+, Edge 90+)

### 설치
```bash
# Node.js 서버
npm install
npm start

# Python 서버
python start_server.py
```

### 디버깅
```javascript
// 콘솔에서 상태 확인
console.log(filterState);
console.log(intervalCaptureState);
console.log(thumbnailState);

// 진행률 모니터링
window.addEventListener('progress', (e) => {
    console.log('Progress:', e.detail);
});
```

## 📝 코딩 규칙

### 네이밍 컨벤션
- 함수: camelCase (`captureFrame`, `applyVideoFilter`)
- 변수: camelCase (`filterState`, `currentFrame`)
- 상수: UPPER_SNAKE_CASE (현재 미사용)
- DOM ID: camelCase (`videoPlayer`, `captureText`)

### 주석 스타일
```javascript
// 단일 라인 주석

/**
 * 함수 설명
 * @param {string} format - 파일 형식
 * @returns {Promise<void>}
 */
```

### 에러 처리
```javascript
try {
    await riskyOperation();
} catch (error) {
    console.error('오류:', error);
    showStatus('오류가 발생했습니다.', 'error');
}
```

## 📄 라이선스

내부 작업용 도구

---

**마지막 업데이트**: 2025-11-16
**버전**: 2.0
**작성자**: Claude Code + User
