"""Original energetic workout beat, synthesized locally for Windows playback.

No downloaded songs or third-party audio files are needed. M toggles music.
"""
import math
import os
import random
import struct
import tempfile
import wave


def make_sport_beat(path, bpm=128, rate=16000):
    """Write a seamless-ish 4-bar electronic fitness loop as a mono PCM WAV."""
    beat = 60.0 / bpm
    duration = 16 * beat
    count = int(duration * rate)
    samples = [0.0] * count
    rng = random.Random(2026)

    def add(start, length, func):
        first = int(start * rate)
        for i in range(min(int(length * rate), count - first)):
            t = i / rate
            samples[first + i] += func(t)

    for step in range(16):
        at = step * beat
        # Four-on-the-floor kick: falling pitch and short punchy decay.
        add(at, 0.27, lambda t: 0.48 * math.exp(-19*t) * math.sin(2*math.pi*(55*t + 85*(1-math.exp(-28*t))/28)))
        if step % 4 in (1, 3):
            noise = [rng.uniform(-1, 1) for _ in range(int(rate * 0.14))]
            add(at, 0.14, lambda t, n=noise: 0.16 * math.exp(-24*t) * n[min(int(t*rate),len(n)-1)])
        # Bright eighth-note hi-hats.
        for half in (0, 0.5):
            h = at + half * beat
            noise = [rng.uniform(-1, 1) for _ in range(int(rate * 0.075))]
            add(h, 0.075, lambda t, n=noise: 0.065 * math.exp(-42*t) * n[min(int(t*rate),len(n)-1)])

    # Four-bar bass riff, A minor, with a gentle pulse and synth lead.
    bass = [110, 110, 130.81, 110, 146.83, 146.83, 130.81, 98,
            110, 110, 164.81, 146.83, 130.81, 130.81, 98, 110]
    lead = [440, 0, 523.25, 0, 587.33, 0, 523.25, 392,
            440, 0, 659.25, 0, 587.33, 523.25, 392, 440]
    for step, (low, high) in enumerate(zip(bass, lead)):
        at = step * beat
        add(at, beat*0.83, lambda t, f=low: 0.15 * min(1, t*65) * math.exp(-3.2*t) *
            (math.sin(2*math.pi*f*t) + 0.27*math.sin(4*math.pi*f*t)))
        if high:
            add(at, beat*0.42, lambda t, f=high: 0.065 * min(1, t*95) * math.exp(-8*t) *
                (math.sin(2*math.pi*f*t) + 0.22*math.sin(4*math.pi*f*t)))

    with wave.open(path, 'wb') as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(rate)
        sound.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, x)) * 24500)) for x in samples))


class WorkoutAudio:
    def __init__(self):
        self.enabled = False
        self._file = None
        self._winsound = None
        try:
            import winsound
            self._winsound = winsound
            fd, path = tempfile.mkstemp(suffix='.wav', prefix='ar_coach_sport_')
            os.close(fd)
            self._file = path
            make_sport_beat(path)
        except (ImportError, OSError):
            self._winsound = None
            self.close()

    def toggle(self):
        if self._winsound is None or not self._file:
            return False
        self.enabled = not self.enabled
        if self.enabled:
            self._winsound.PlaySound(self._file, self._winsound.SND_FILENAME | self._winsound.SND_ASYNC | self._winsound.SND_LOOP)
        else:
            self._winsound.PlaySound(None, 0)
        return self.enabled

    def notify(self):
        if self._winsound:
            self._winsound.MessageBeep(self._winsound.MB_ICONASTERISK)

    def close(self):
        if self._winsound:
            self._winsound.PlaySound(None, 0)
        self.enabled = False
        if self._file:
            try:
                os.unlink(self._file)
            except OSError:
                pass
            self._file = None
