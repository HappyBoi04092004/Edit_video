import json
import math
import numpy as np
import wave

SR = 48000
DUR = 40.0
total_samples = int(SR * DUR)
buf = np.zeros(total_samples, dtype=np.float32)
t_axis = np.arange(total_samples) / SR

# 1. Warm Ambient Hi-Tech Drone (Continuous 40s pad)
drone_f1 = 55.0   # A1
drone_f2 = 110.0  # A2
drone_f3 = 164.81 # E3
drone = (
    0.18 * np.sin(2 * np.pi * drone_f1 * t_axis) +
    0.12 * np.sin(2 * np.pi * drone_f2 * t_axis) +
    0.08 * np.sin(2 * np.pi * drone_f3 * t_axis)
)
# Gentle pulse modulation (lfo)
lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t_axis)
drone *= lfo
buf += drone

# Helper functions for procedural sound effects
def env(n, dec):
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / 0.005)
    return a * np.exp(-t / dec)

def sweep(f0, f1, d, dec, shape=np.sin):
    n = int(SR * d)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return shape(ph) * env(n, dec)

def chord(freqs, d, dec=0.5):
    n = int(SR * d)
    t = np.arange(n) / SR
    sig = np.zeros(n, dtype=np.float32)
    for f in freqs:
        sig += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    sig /= len(freqs)
    return sig * env(n, dec)

def inject(sig, start_t, gain=0.5):
    i = int(start_t * SR)
    n = len(sig)
    if i >= total_samples:
        return
    j = min(total_samples, i + n)
    buf[i:j] += (sig[:j - i] * gain).astype(np.float32)

# --- Event Schedule Across 40 Seconds ---

# 0s - 4.5s: Office Intro & Hub Opening
for tk in [0.8, 1.2, 1.6, 2.1, 2.4, 2.8, 3.2, 3.7]:
    inject(sweep(1800, 1400, 0.03, 0.008), tk, 0.08) # keyboard clicks
inject(chord([440, 554.37, 659.25], 1.2, 0.6), 2.2, 0.35) # A major login chime

# 4.5s - 9.5s: Campaign Creation (Elena)
for tk in [5.2, 5.5, 5.9, 6.2, 6.8, 7.1]:
    inject(sweep(2200, 1800, 0.025, 0.006), tk, 0.08)
inject(sweep(600, 1200, 0.18, 0.08), 7.5, 0.3) # YouTube select
inject(sweep(700, 1400, 0.18, 0.08), 8.2, 0.3) # Web select
inject(chord([523.25, 659.25, 783.99, 1046.50], 1.5, 0.7), 9.0, 0.45) # Deploy harvest chime

# 9.5s - 15.0s: Crawler Activation (Marcus & Servers)
inject(sweep(120, 240, 0.8, 0.4), 10.2, 0.4) # Crawler switch thud
# Server cluster hum escalation
hum_n = int(SR * 4.5)
hum_t = np.arange(hum_n) / SR
crawler_hum = 0.25 * np.sin(2 * np.pi * (120 + 30 * hum_t / 4.5) * hum_t) * env(hum_n, 2.5)
inject(crawler_hum, 10.5, 0.4)
for st in np.arange(11.0, 14.8, 0.45):
    inject(sweep(2400, 2400, 0.02, 0.005), st, 0.12) # Server LED blips

# 15.0s - 25.0s: The Data Journey Through Architecture
# Rhythmic high-tech pulse packets
for pt in np.arange(15.2, 24.8, 0.38):
    freq = 880 + (int(pt * 2) % 4) * 220
    inject(sweep(freq, freq * 0.7, 0.06, 0.02), pt, 0.22)
    # Sub bass heartbeat
    if int(pt / 0.38) % 2 == 0:
        inject(sweep(90, 45, 0.15, 0.05), pt, 0.35)

# Normalizer laser sweep (20.0s - 22.5s)
laser_n = int(SR * 2.2)
laser_t = np.arange(laser_n) / SR
laser = 0.2 * np.sin(2 * np.pi * (600 + 300 * np.sin(2 * np.pi * 3 * laser_t)) * laser_t) * env(laser_n, 1.2)
inject(laser, 20.2, 0.3)

# MySQL write commit thuds (23.0s, 23.8s, 24.5s)
for mt in [23.0, 23.8, 24.5]:
    inject(sweep(140, 70, 0.25, 0.08), mt, 0.4)
    inject(sweep(1800, 1800, 0.04, 0.01), mt + 0.05, 0.2)

# 25.0s - 31.0s: QA Validation & Approval (Maya)
for qt in [26.0, 26.8, 27.5]:
    inject(sweep(1400, 1400, 0.05, 0.01), qt, 0.15)
# Golden approval signature chime at 28.5s (D major high crystalline arpeggio)
for idx, fn in enumerate([587.33, 739.99, 880.0, 1174.66]):
    inject(chord([fn, fn * 1.5], 1.2, 0.6), 28.5 + idx * 0.12, 0.4)

# 31.0s - 36.0s: Central Wall Screen Power On & Celebration
# Grand majestic chord (C Major add 9)
inject(chord([261.63, 329.63, 392.00, 587.33, 783.99], 3.5, 1.8), 31.5, 0.55)
# Real-time data streaming sparkle
for st in np.arange(32.5, 35.8, 0.25):
    inject(sweep(1600 + (st % 1) * 800, 1200, 0.04, 0.01), st, 0.15)

# 36.0s - 40.0s: Grand Pull-back & Logo Reveal
# Final deep warm cinematic chord resolving to tonic (F major / C major)
inject(chord([130.81, 196.00, 261.63, 329.63, 392.00, 523.25], 4.2, 2.2), 36.2, 0.6)
# Gentle sub drop
inject(sweep(80, 40, 1.5, 0.8), 36.5, 0.45)

# Soft master limiting & stereo panning
buf = np.tanh(buf * 1.15) * 0.85
# Tail fade out in final 0.6 seconds
fade_len = int(SR * 0.6)
buf[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)

# Stereo widening (slight delay on right channel for spatial depth)
delay_samples = int(SR * 0.015) # 15ms delay
right_buf = np.zeros_like(buf)
right_buf[delay_samples:] = buf[:-delay_samples]

stereo = np.stack([buf, right_buf], axis=1)
pcm = (stereo * 32767.0).astype('<i2')

out_path = r"d:\animasyon-stil-katalogu\social-data-hub\soundtrack.wav"
w = wave.open(out_path, 'wb')
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(SR)
w.writeframes(pcm.tobytes())
w.close()
print(f"Generated pristine 40s stereo soundtrack: {out_path} ({len(pcm)} frames)")
