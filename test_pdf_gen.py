"""Tests for the M3U8 Transcript Generator."""

import os

import pytest

from pdf_writer import create_pdf, format_seconds
from transcriber import VALID_MODELS
from writers import write_pdf, write_srt, write_txt, write_transcript, SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_SEGMENTS = [
    {"start": 0.0, "end": 5.0, "text": " This is the first segment."},
    {"start": 5.0, "end": 12.5, "text": " A longer segment to test text wrapping behaviour."},
    {"start": 15.0, "end": 20.0, "text": " Final segment."},
]

SAMPLE_METADATA = {
    "source_url": "https://example.com/stream.m3u8",
    "date": "2025-01-01 12:00:00",
    "model": "base",
    "language": "en",
}


# ---------------------------------------------------------------------------
# format_seconds
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


# ---------------------------------------------------------------------------
# PDF writer (backward-compat + new)
# ---------------------------------------------------------------------------

class TestCreatePdf:
    def test_creates_file(self, tmp_path):
        output = str(tmp_path / "test.pdf")
        create_pdf(SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_empty_segments(self, tmp_path):
        output = str(tmp_path / "empty.pdf")
        create_pdf([], output)
        assert os.path.exists(output)

    def test_write_pdf_with_metadata(self, tmp_path):
        output = str(tmp_path / "meta.pdf")
        write_pdf(SAMPLE_SEGMENTS, output, metadata=SAMPLE_METADATA)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0


# ---------------------------------------------------------------------------
# SRT writer
# ---------------------------------------------------------------------------

class TestWriteSrt:
    def test_creates_file(self, tmp_path):
        output = str(tmp_path / "test.srt")
        write_srt(SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)

    def test_content_structure(self, tmp_path):
        output = str(tmp_path / "test.srt")
        write_srt(SAMPLE_SEGMENTS, output)
        content = open(output, encoding="utf-8").read()
        # SRT files have numbered entries
        assert "1\n" in content
        assert "-->" in content
        assert "This is the first segment." in content

    def test_empty_segments(self, tmp_path):
        output = str(tmp_path / "empty.srt")
        write_srt([], output)
        assert os.path.exists(output)
        assert os.path.getsize(output) == 0


# ---------------------------------------------------------------------------
# TXT writer
# ---------------------------------------------------------------------------

class TestWriteTxt:
    def test_creates_file(self, tmp_path):
        output = str(tmp_path / "test.txt")
        write_txt(SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)

    def test_content_contains_timestamps(self, tmp_path):
        output = str(tmp_path / "test.txt")
        write_txt(SAMPLE_SEGMENTS, output)
        content = open(output, encoding="utf-8").read()
        assert "[0:00:00 - 0:00:05]" in content
        assert "This is the first segment." in content

    def test_metadata_header(self, tmp_path):
        output = str(tmp_path / "meta.txt")
        write_txt(SAMPLE_SEGMENTS, output, metadata=SAMPLE_METADATA)
        content = open(output, encoding="utf-8").read()
        assert "Source: https://example.com/stream.m3u8" in content
        assert "Model:  base" in content


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

class TestWriteTranscript:
    def test_pdf_dispatch(self, tmp_path):
        output = str(tmp_path / "dispatch.pdf")
        write_transcript("pdf", SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)

    def test_srt_dispatch(self, tmp_path):
        output = str(tmp_path / "dispatch.srt")
        write_transcript("srt", SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)

    def test_txt_dispatch(self, tmp_path):
        output = str(tmp_path / "dispatch.txt")
        write_transcript("txt", SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)

    def test_unsupported_format(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported format"):
            write_transcript("docx", SAMPLE_SEGMENTS, str(tmp_path / "bad.docx"))

    def test_case_insensitive(self, tmp_path):
        output = str(tmp_path / "upper.pdf")
        write_transcript("PDF", SAMPLE_SEGMENTS, output)
        assert os.path.exists(output)


# ---------------------------------------------------------------------------
# Transcriber validation
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


# ---------------------------------------------------------------------------
# URL validation
# ---------------------------------------------------------------------------

class TestDownloadValidation:
    def test_empty_url(self):
        from transcriber import download_audio
        with pytest.raises(ValueError, match="empty"):
            download_audio("", "/tmp/test.mp3")

    def test_invalid_scheme(self):
        from transcriber import download_audio
        with pytest.raises(ValueError, match="http"):
            download_audio("ftp://example.com/stream.m3u8", "/tmp/test.mp3")
