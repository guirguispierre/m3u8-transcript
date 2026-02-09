"""Tests for the M3U8 Transcript Generator."""

import os
import tempfile

import pytest

from pdf_writer import create_pdf, format_seconds
from transcriber import VALID_MODELS


# ---------------------------------------------------------------------------
# pdf_writer tests
# ---------------------------------------------------------------------------

class TestFormatSeconds:
    def test_zero(self):
        assert format_seconds(0) == "0:00:00"

    def test_exact_minute(self):
        assert format_seconds(60) == "0:01:00"

    def test_hour_plus(self):
        assert format_seconds(3661) == "1:01:01"

    def test_float_truncated(self):
        assert format_seconds(5.9) == "0:00:05"


class TestCreatePdf:
    SAMPLE_SEGMENTS = [
        {"start": 0.0, "end": 5.0, "text": " This is the first segment."},
        {"start": 5.0, "end": 12.5, "text": " A longer segment to test text wrapping behaviour."},
        {"start": 15.0, "end": 20.0, "text": " Final segment."},
    ]

    def test_creates_file(self, tmp_path):
        output = str(tmp_path / "test.pdf")
        create_pdf(self.SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_empty_segments(self, tmp_path):
        output = str(tmp_path / "empty.pdf")
        create_pdf([], output)
        assert os.path.exists(output)


# ---------------------------------------------------------------------------
# transcriber validation tests
# ---------------------------------------------------------------------------

class TestValidModels:
    def test_expected_models(self):
        assert VALID_MODELS == {"tiny", "base", "small", "medium", "large"}

    def test_invalid_model_rejected(self):
        from transcriber import transcribe_audio
        with pytest.raises(ValueError, match="Invalid model"):
            transcribe_audio("/nonexistent.mp3", model_name="nonexistent")

    def test_missing_audio_file(self):
        from transcriber import transcribe_audio
        with pytest.raises(FileNotFoundError):
            transcribe_audio("/absolutely/does/not/exist.mp3", model_name="base")
