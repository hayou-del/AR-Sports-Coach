import wave
from ui.audio import make_sport_beat


def test_generated_sport_beat_is_valid_wav(tmp_path):
    path = tmp_path / 'sport.wav'
    make_sport_beat(str(path))
    with wave.open(str(path), 'rb') as sound:
        assert sound.getframerate() == 16000
        assert sound.getnchannels() == 1
        assert sound.getnframes() > 100000
