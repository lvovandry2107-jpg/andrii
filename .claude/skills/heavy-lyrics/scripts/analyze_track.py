#!/usr/bin/env python3
"""Analyze an instrumental for lyric writing: tempo (incl. tempo changes),
bar grid, energy, repeated bars/riffs, and where the music ends.

Usage:  python3 -I analyze_track.py <audio file> [--bpm-hint 130]
Needs:  pip install librosa   (ffmpeg for mp3 is usually present)

Output is plain text for Claude to interpret; it is a hypothesis, not ground
truth - always ask the user to confirm section names.
"""
import argparse
import warnings

import numpy as np

warnings.filterwarnings("ignore")
import librosa  # noqa: E402

HOP = 512
SR = 22050


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def acf_tempo(seg, sr):
    """Strongest tempo candidates of a slice via onset autocorrelation."""
    o = librosa.onset.onset_strength(y=seg, sr=sr, hop_length=HOP)
    ac = librosa.autocorrelate(o, max_size=400)
    out = []
    for lag in range(10, len(ac) - 2):
        bpm = 60 * sr / HOP / lag
        if 60 < bpm < 200 and ac[lag] == ac[lag - 2:lag + 3].max():
            out.append((round(bpm, 1), ac[lag]))
    out.sort(key=lambda x: -x[1])
    return [b for b, _ in out[:3]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--bpm-hint", type=float, default=120.0)
    ap.add_argument("--window", type=float, default=10.0, help="seconds per tempo window")
    ap.add_argument("--sim", type=float, default=0.985, help="bar similarity threshold")
    a = ap.parse_args()

    y, sr = librosa.load(a.path, sr=SR, mono=True)
    dur = len(y) / sr
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP)
    loud = np.where(rms > 0.01)[0]
    music_start = times[loud[0]] if len(loud) else 0.0
    music_end = times[loud[-1]] if len(loud) else dur
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)

    print(f"file duration {mmss(dur)} | music {mmss(music_start)}-{mmss(music_end)}")
    gt = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr, start_bpm=a.bpm_hint))[0])
    print(f"global tempo ~{gt:.1f} BPM\n")

    print("== Tempo / energy per window (watch for tempo changes; half/double values are common) ==")
    for s in np.arange(music_start, music_end, a.window):
        e = min(music_end, s + a.window)
        if e - s < 4:
            continue
        seg = y[int(s * sr):int(e * sr)]
        print(f"{mmss(s)}  tempo candidates {acf_tempo(seg, sr)}  rms {librosa.feature.rms(y=seg)[0].mean():.3f}")

    print("\n== Bars (4 beats) with repetition labels ==")
    print("Same letter = similar sound (same riff). Low rms bars between loud ones = stops/holes.")
    _, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP, start_bpm=a.bpm_hint)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=HOP, n_mfcc=13)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP)[0]
    bars = beats[::4]
    feats, info = [], []
    for i in range(len(bars) - 1):
        s, e = bars[i], bars[i + 1]
        c = chroma[:, s:e].mean(1)
        feats.append(np.concatenate([c / (c.max() + 1e-9), mfcc[1:, s:e].mean(1) / 50]))
        info.append((librosa.frames_to_time(s, sr=sr, hop_length=HOP),
                     librosa.frames_to_time(e, sr=sr, hop_length=HOP),
                     rms[s:e].mean(), oenv[s:e].mean(), cent[s:e].mean()))
    if not feats:
        print("no bars detected")
        return
    F = np.array(feats)
    F /= np.linalg.norm(F, axis=1, keepdims=True)
    reps, labels = [], []
    for f in F:
        sims = [f @ r for r in reps]
        if sims and max(sims) > a.sim:
            labels.append(int(np.argmax(sims)))
        else:
            reps.append(f)
            labels.append(len(reps) - 1)

    def name(k):
        return chr(65 + k % 26) + (str(k // 26) if k >= 26 else "")

    for i, ((t0, t1, r, o, c), k) in enumerate(zip(info, labels), 1):
        bpm = 240 / (t1 - t0) if t1 > t0 else 0
        print(f"bar{i:3d} {mmss(t0)} ({t1 - t0:4.2f}s ~{bpm:5.1f}bpm) {name(k):3s} rms {r:.3f} onset {o:.2f} bright {c:5.0f}")


if __name__ == "__main__":
    main()
