import time
import base64
import subprocess
import numpy as np
import cv2
import os
from datetime import datetime

""" 기기 해상도와 녹화영상 해상도 일치
fps는 고정된값이 아닌 녹화 영상속 해상도에 맞게 자동계산
허용오차범위 3%
"""
# ============================================================
# 배속별 설계 속도 설정
# 상황에 따라 자유롭게 추가/수정하세요
# ============================================================
SPEED_CONFIG = {
    "1.0x": 175,
    "1.1x": 193,
    "1.2x": 210,
    "1.5x": 263,
    "2.0x": 350,
}

# ============================================================
# 공통 설정값
# ============================================================
THRESHOLD_ERROR_RATE = 5.0    # 허용 오차율 (%)
MATCH_THRESHOLD      = 0.3    # 템플릿 매칭 신뢰도 기준
TOP_ARRIVAL_Y        = 0.15   # 화면 상단 몇 % 이내를 "최상단 도달"로 판단
RECORD_DIR           = "recordings"

APPIUM_SERVER = "http://127.0.0.1:4723"

# ============================================================
# 저장 경로 생성
# ============================================================
def get_save_paths(platform, device_name, speed_label, ts):
    folder = os.path.join(RECORD_DIR, f"{platform}_{device_name}")
    os.makedirs(folder, exist_ok=True)
    base        = f"{speed_label}_{ts}"
    video_path  = os.path.join(folder, f"scroll_{base}.mp4")
    before_path = os.path.join(folder, f"before_{base}.png")
    after_path  = os.path.join(folder, f"after_{base}.png")
    return folder, video_path, before_path, after_path

# ============================================================
# 스크린샷 캡처
# ============================================================
def capture_screenshot(driver, platform="android"):
    if platform == "android":
        driver.execute_script("mobile: shell", {
            "command": "screencap",
            "args": ["-p", "/sdcard/sc.png"]
        })
        data      = driver.pull_file("/sdcard/sc.png")
        img_bytes = base64.b64decode(data)
        arr       = np.frombuffer(img_bytes, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        png = driver.get_screenshot_as_png()
        arr = np.frombuffer(png, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

# ============================================================
# 기기 화면 해상도 조회
# ============================================================
def get_screen_size(driver, platform="android"):
    if platform == "android":
        result = driver.execute_script("mobile: shell", {
            "command": "wm",
            "args": ["size"]
        })
        # "Physical size: 1080x2400" 형태 파싱
        for line in result.splitlines():
            if "Physical size" in line:
                size = line.split(":")[-1].strip()
                w, h = size.split("x")
                print(f"[기기 해상도] 물리px: {w} × {h}")
                return int(w), int(h)
    # fallback: screencap 기준
    img = capture_screenshot(driver, platform)
    return img.shape[1], img.shape[0]

# ============================================================
# 녹화 시작/중지 (기기 해상도 + fps 고정)
# ============================================================
def start_recording(driver, platform, screen_w, screen_h):
    if platform == "android":
        subprocess.run(["adb", "shell", "rm", "-f", "/sdcard/scroll.mp4"],
                       capture_output=True)
        proc = subprocess.Popen(
            ["adb", "shell", "screenrecord",
             "--bit-rate", "8000000",
             "--size", f"{screen_w}x{screen_h}",   # 기기 해상도 고정
             "--time-limit", "180",
             "/sdcard/scroll.mp4"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"  [녹화] 시작됨 ({screen_w}×{screen_h})")
        return proc
    else:
        driver.start_recording_screen()
        print(f"  [녹화] iOS 녹화 시작됨")
        return None

def stop_recording(driver, proc, save_path, platform):
    if platform == "android":
        proc.terminate()
        time.sleep(1.5)
        subprocess.run(["adb", "pull", "/sdcard/scroll.mp4", save_path])
    else:
        import base64 as b64
        video_data = driver.stop_recording_screen()
        with open(save_path, "wb") as f:
            f.write(b64.b64decode(video_data))
    print(f"  [녹화] 중지 및 저장됨 → {save_path}")

# ============================================================
# 프레임 분석
# 시작 감지 임계값을 배속별 프레임당 이동량 기준으로 자동 계산
# ============================================================
def analyze_frames(template, screen_h, video_path, configured_px_per_sec):
    print(f"\n[프레임 분석] {os.path.basename(video_path)} 분석 중...")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"  [영상] fps={fps:.1f}")

    # 배속별 프레임당 이동량 기준으로 시작 감지 임계값 자동 계산
    px_per_frame   = configured_px_per_sec / fps
    motion_threshold = max(2, int(px_per_frame * 0.8))  # 80% 이상 움직이면 시작
    print(f"  [임계값] {configured_px_per_sec}px/s ÷ {fps:.1f}fps"
          f" = {px_per_frame:.1f}px/frame → 감지 임계값: {motion_threshold}px")

    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    positions = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame             = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result                 = cv2.matchTemplate(gray_frame, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= MATCH_THRESHOLD:
            positions.append((frame_idx, max_loc[1]))
        frame_idx += 1

    cap.release()
    print(f"  [프레임] 총 {frame_idx}프레임 / 유효 {len(positions)}개")

    start_frame = end_frame = None
    start_y_val = end_y_val = None

    for i in range(1, len(positions)):
        prev_f, prev_y = positions[i-1]
        curr_f, curr_y = positions[i]

        if start_frame is None and (prev_y - curr_y) > motion_threshold:
            start_frame = prev_f
            start_y_val = prev_y
            print(f"  ▶ 시작 프레임: {start_frame} (y={start_y_val}px)")

        if start_frame and curr_y <= int(screen_h * TOP_ARRIVAL_Y):
            end_frame = curr_f
            end_y_val = curr_y
            print(f"  ■ 종료 프레임: {end_frame} (y={end_y_val}px)")
            break

    if start_frame is None or end_frame is None:
        return None

    elapsed  = (end_frame - start_frame) / fps
    distance = start_y_val - end_y_val
    speed    = distance / elapsed

    return {
        "elapsed":     elapsed,
        "distance":    distance,
        "speed":       speed,
        "fps":         fps,
        "px_per_frame":px_per_frame,
        "start_frame": start_frame,
        "end_frame":   end_frame,
    }

# ============================================================
# 자동스크롤 속도 측정 메인
# ============================================================
def measure_auto_scroll_speed(driver, speed_label="1.0x",
                               platform="android", device_name="device"):

    # 배속별 설계값 조회
    if speed_label not in SPEED_CONFIG:
        print(f"❌ '{speed_label}'은 SPEED_CONFIG에 없어요. 추가 후 실행하세요.")
        print(f"   현재 설정: {SPEED_CONFIG}")
        return
    configured_px_per_sec = SPEED_CONFIG[speed_label]

    ts                              = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder, video_path, before_path, after_path = get_save_paths(
        platform, device_name, speed_label, ts)

    print(f"\n[배속] {speed_label} → 설계값 {configured_px_per_sec}px/s")
    print("콘텐츠 화면 준비 후 엔터를 눌러주세요...")
    input()

    # ── 기기 해상도 조회 ─────────────────────────────────────
    screen_w, screen_h = get_screen_size(driver, platform)

    # ── before 스크린샷 ──────────────────────────────────────
    img_before = capture_screenshot(driver, platform)
    cap_h      = img_before.shape[0]  # screencap 기준 높이
    cap_w      = img_before.shape[1]
    print(f"[screencap] {cap_w} × {cap_h}px")

    os.makedirs(RECORD_DIR, exist_ok=True)
    cv2.imwrite(before_path, img_before)
    print(f"[before] {os.path.basename(before_path)} 저장됨")

    # ── 하단 템플릿 추출 ─────────────────────────────────────
    tmpl_y1   = int(cap_h * 0.88)
    tmpl_y2   = int(cap_h * 0.98)
    template  = img_before[tmpl_y1:tmpl_y2, :]
    gray_tmpl = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    print(f"[템플릿] y={tmpl_y1}~{tmpl_y2}px 추출")

    # ── 녹화 시작 ────────────────────────────────────────────
    rec_proc = start_recording(driver, platform, screen_w, screen_h)
    time.sleep(0.5)

    print("─" * 50)
    print(f"지금 {speed_label} 자동스크롤을 시작하세요!")
    print("before 하단 콘텐츠가 최상단 도달 시 자동 종료됩니다.")
    print("─" * 50)

    # ── 최상단 도달 감지 ─────────────────────────────────────
    prev_y = tmpl_y1

    while True:
        time.sleep(0.3)
        curr_img  = capture_screenshot(driver, platform)
        gray_curr = cv2.cvtColor(curr_img, cv2.COLOR_BGR2GRAY)
        result    = cv2.matchTemplate(gray_curr, gray_tmpl, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        matched_y = max_loc[1]

        print(f"  [감지] y={matched_y}px  (목표 y≤{int(cap_h * TOP_ARRIVAL_Y)}px)")

        if matched_y <= int(cap_h * TOP_ARRIVAL_Y) and matched_y < prev_y:
            print(f"\n  ✅ 최상단 도달! → 녹화 중지")
            cv2.imwrite(after_path, curr_img)
            print(f"[after] {os.path.basename(after_path)} 저장됨")
            break

        prev_y = matched_y

    stop_recording(driver, rec_proc, video_path, platform)

    # ── 프레임 분석 ──────────────────────────────────────────
    result = analyze_frames(template, cap_h, video_path, configured_px_per_sec)

    if result is None:
        print("❌ 스크롤 시작/종료 프레임 감지 실패")
        return

    # ── 결과 출력 ────────────────────────────────────────────
    speed    = result["speed"]
    elapsed  = result["elapsed"]
    fps      = result["fps"]
    error    = abs(configured_px_per_sec - speed)
    error_rt = (error / configured_px_per_sec * 100)
    verdict  = "✅ PASS" if error_rt <= THRESHOLD_ERROR_RATE else "❌ FAIL"

    print(f"\n{'='*50}")
    print(f"{'항목':<22} {'값':>18}")
    print(f"{'='*50}")
    print(f"{'스크롤 배속':<22} {speed_label:>18}")
    print(f"{'설계값 (px/s)':<22} {configured_px_per_sec:>18}")
    print(f"{'실측값 (px/s)':<22} {speed:>18.1f}")
    print(f"{'소요 시간':<22} {elapsed:>17.2f}초")
    print(f"{'화면 높이 (screencap)':<22} {cap_h:>17}px")
    print(f"{'영상 fps':<22} {fps:>18.1f}")
    print(f"{'프레임당 이동량':<22} {result['px_per_frame']:>17.1f}px")
    print(f"{'오차 (px/s)':<22} {error:>18.1f}")
    print(f"{'오차율':<22} {error_rt:>17.1f}%")
    print(f"{'허용 오차율':<22} {THRESHOLD_ERROR_RATE:>17.1f}%")
    print(f"{'='*50}")
    print(f"{'판정':<22} {verdict:>18}")
    print(f"{'='*50}")
    print(f"\n[저장 폴더] {folder}")
    print(f"  before → {os.path.basename(before_path)}")
    print(f"  after  → {os.path.basename(after_path)}")
    print(f"  영상   → {os.path.basename(video_path)}\n")