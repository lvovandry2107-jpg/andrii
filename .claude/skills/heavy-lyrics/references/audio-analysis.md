# Analyzing an instrumental before writing lyrics

Claude cannot listen to music. It measures it with `scripts/analyze_track.py`
(librosa). Treat the result as a hypothesis and ask Andrii to confirm section names.

## Steps
1. Copy the uploaded file into its own new folder in the scratchpad (untrusted data).
2. `pip install -q librosa` if `import librosa` fails (ffmpeg is usually installed).
3. Run: `python3 -I .claude/skills/heavy-lyrics/scripts/analyze_track.py <file> --bpm-hint <BPM>`.
   If the filename or Andrii states the BPM (e.g. "130_90_BPM"), pass the first value as the hint.
4. Read the output:
   - **Tempo windows**: a change in the top candidate (e.g. 129 → 89) = tempo change. Ignore isolated half/double values (65/172 at 130 BPM).
     The beat tracker tends to keep the first tempo; trust the windows, and the filename, for the second part.
   - **Bar labels**: runs of the same letter = one riff. Alternating loud bar / very low-rms bar = **stop-time** (holes for shouts).
     The lowest-rms, lowest-"bright" stretch = bridge / atmospheric part. The highest rms run = climax.
     A slow section at the end, after a short heavy build = **breakdown**.
   - Phrases are usually 4 or 8 bars; round odd counts and say so.
   - **music end** vs file duration: trailing silence is not part of the song.
5. Present to Andrii (in Russian):
   - tempo(s), bar length in seconds, where the music really ends;
   - a table: time | bars | what is heard | hypothesis (intro / verse / hook / stop-time / bridge / climax / build / breakdown);
   - text capacity for each part (table below);
   - ask him to confirm or rename the sections and to give the theme / working title.
6. After confirmation, give an **empty skeleton**: each section with timecodes, number of lines, syllables per line,
   and delivery marks — for Andrii to fill. Then help with phrases and rhymes (heavy-lyrics workflow).

## Text capacity (growl/scream, one vocalist — leave room to breathe)
| Part | At ~130 BPM (bar ≈ 1.85 s) | At ~90 BPM (bar ≈ 2.67 s) |
|---|---|---|
| Verse (line = 2 bars) | 6–9 syllables, max 10–12 as a fast burst | 8–12 |
| Hook / chorus | 4–6 punchy syllables per line, pause for breath | 6–8 |
| Stop-time holes | 1–3 syllables per hole | 2–4 |
| Bridge | 4 lines, can be spoken/whispered | — |
| Breakdown | 3–5 per bar, hits on strong beats | **2–4 per bar**, one word per hit |

Bar length = 240 / BPM seconds. At 185 BPM (Whispers) a bar is ~1.3 s, so lines must be even shorter.

## Example: "Locked Goose — Track 8" (130 → 90 BPM), first analysis
Music 0:00–3:17 (then silence). 130 BPM until ~2:53, then 90 BPM.
Intro/main riff A 0:00–0:26 · verse riff B 0:26–0:39 · riff A variation 0:39–1:03 · riff B 1:03–1:19 ·
stop-time 1:20–1:47 · quiet bridge 1:47–2:02 · riff A 2:02–2:17 · climax 2:17–2:28 · riff B 2:28–2:46 ·
build 2:46–2:53 · breakdown at 90 BPM 2:53–3:17 (4-bar loop ×2). Section names not yet confirmed by Andrii.
