import os
import sys
import time
import base64
import subprocess
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

TOTAL_SECONDS = 40.0
FPS = 30
TOTAL_FRAMES = int(TOTAL_SECONDS * FPS) # 1200 frames
NUM_WORKERS = 4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(BASE_DIR, "frames")
HTML_PATH = os.path.join(BASE_DIR, "anim.html").replace(os.sep, "/")
WAV_PATH = os.path.join(BASE_DIR, "soundtrack.wav")
OUT_VIDEO = os.path.join(BASE_DIR, "social_data_hub.mp4")

os.makedirs(FRAMES_DIR, exist_ok=True)

print(f"==================================================")
print(f"SOCIAL DATA HUB – THE DATA JOURNEY (40s)")
print(f"Total Frames: {TOTAL_FRAMES} | FPS: {FPS} | Workers: {NUM_WORKERS}")
print(f"==================================================")

# Step 1: Synthesize Audio
print("\n[Step 1/3] Synthesizing 40-second procedural audio...")
synth_script = os.path.join(BASE_DIR, "synth.py")
subprocess.run([sys.executable, synth_script], check=True)

# Step 2: Render all 1200 frames with Playwright Chrome
print(f"\n[Step 2/3] Rendering {TOTAL_FRAMES} Full HD 1920x1080 frames...")
t_start = time.time()

# Distribute frame indices across workers
worker_chunks = [[] for _ in range(NUM_WORKERS)]
for frame_idx in range(TOTAL_FRAMES):
    worker_chunks[frame_idx % NUM_WORKERS].append(frame_idx)

completed_count = 0

def render_worker(worker_id, frame_list):
    global completed_count
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file:///{HTML_PATH}")
        page.wait_for_function("() => window.ready")

        for f_idx in frame_list:
            t = f_idx / FPS
            b64 = page.evaluate(f"window.draw({{ t: {t} }})")
            img_data = base64.b64decode(b64)
            out_file = os.path.join(FRAMES_DIR, f"{f_idx:05d}.jpg")
            with open(out_file, "wb") as f:
                f.write(img_data)
            completed_count += 1
            if completed_count % 100 == 0 or completed_count == TOTAL_FRAMES:
                pct = (completed_count / TOTAL_FRAMES) * 100
                elapsed = time.time() - t_start
                fps_render = completed_count / elapsed
                print(f"Progress: {completed_count}/{TOTAL_FRAMES} frames ({pct:.1f}%) | {fps_render:.1f} fps rendered | {elapsed:.1f}s")
        browser.close()

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    futures = [
        executor.submit(render_worker, w_id, worker_chunks[w_id])
        for w_id in range(NUM_WORKERS)
    ]
    for future in futures:
        future.result()

render_time = time.time() - t_start
print(f"\nRendered {TOTAL_FRAMES} frames in {render_time:.1f} seconds! ({TOTAL_FRAMES/render_time:.1f} fps)")

# Step 3: Compile MP4 with FFMPEG
print(f"\n[Step 3/3] Encoding MP4 H.264 video with ffmpeg...")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "%05d.jpg"),
    "-i", WAV_PATH,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    "-preset", "medium",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUT_VIDEO
]

res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFMPEG error:", res.stderr)
    sys.exit(res.returncode)

size_mb = os.path.getsize(OUT_VIDEO) / (1024 * 1024)
print(f"\n==================================================")
print(f"SUCCESS! Continuous 40s film delivered:")
print(f"File: {OUT_VIDEO}")
print(f"Size: {size_mb:.2f} MB")
print(f"Resolution: 1920x1080 | 30 FPS | H.264 MP4 | Stereo Audio")
print(f"==================================================")
