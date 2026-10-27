# AR Sports Coach

A Python/OpenCV/MediaPipe **real-time squat coaching prototype** featuring a neon-style full-screen dashboard, webcam pose tracking, squat repetition counting, rule-based coaching, custom workout goals and synthesized sports music.

## Quick start (Windows, Python 3.11)

Open PowerShell in the folder containing `live_demo.py`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe live_demo.py
```

Options: `python live_demo.py --no-setup` skips goal selection; `--camera 1` selects another webcam.

## Controls

| Key | Action |
|---|---|
| Q | Quit |
| R | Reset workout |
| P | Pause/resume |
| L | Switch tracked leg (resets analysis) |
| M | Toggle sports music |
| F or Esc | Toggle full-screen |

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for module responsibilities and data flow, and [docs/](docs/) for detailed interfaces.

## Scope

Squat tracking only. Coaching is rule-based, and calorie figures are **illustrative placeholders**, not actual energy measurements or health advice. Webcam and audio playback should be checked on the presentation PC. `main.py` is a non-camera example; `live_demo.py` launches the live app.

Developed as a collaborative team project. Preserve contributors' attribution when publishing.
