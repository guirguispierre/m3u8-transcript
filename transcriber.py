"""Audio downloading and transcription utilities."""

import logging
import os
import subprocess
import tempfile
from typing import Any, Dict, Optional

import whisper

log = logging.getLogger(__name__)

VALID_MODELS = {"tiny", "base", "small", "medium", "large"}

# ---------------------------------------------------------------------------
# Model cache -- avoids reloading the same Whisper model repeatedly
# ---------------------------------------------------------------------------
_model_cache: Dict[str, Any] = {}


def make_temp_audio_path() -> str:
    """Create a unique temporary file path for audio downloads."""
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    return path


def download_audio(m3u8_url: str, output_path: str) -> str:
    """
    Download audio from an m3u8 stream and save it as an MP3 file using yt-dlp.

    Args:
        m3u8_url: The URL to download audio from.
        output_path: Destination file path for the MP3.

    Returns:
        The path to the downloaded MP3 file.

    Raises:
        ValueError: If the URL is empty or clearly invalid.
        FileNotFoundError: If yt-dlp completes but the output file is missing.
        subprocess.CalledProcessError: If yt-dlp exits with a non-zero code.
    """
    if not m3u8_url or not m3u8_url.strip():
        raise ValueError("URL cannot be empty.")

    m3u8_url = m3u8_url.strip()
    if not m3u8_url.startswith(("http://", "https://")):
        raise ValueError(
            f"Invalid URL (must start with http:// or https://): {m3u8_url}"
        )

    log.info("Downloading audio from %s using yt-dlp...", m3u8_url)

    base_name = os.path.splitext(output_path)[0]

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", f"{base_name}.%(ext)s",
        "--force-overwrites",
        "--no-check-certificates",
        m3u8_url,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        log.error("yt-dlp failed: %s", exc)
        raise

    expected_file = f"{base_name}.mp3"
    if os.path.exists(expected_file):
        log.info("Audio saved to %s", expected_file)
        return expected_file

    raise FileNotFoundError(
        f"yt-dlp finished but {expected_file} was not found."
    )


def _load_model(model_name: str) -> Any:
    """Load (or return cached) Whisper model."""
    if model_name in _model_cache:
        log.debug("Using cached Whisper model '%s'", model_name)
        return _model_cache[model_name]

    log.info("Loading Whisper model '%s'...", model_name)
    model = whisper.load_model(model_name)
    _model_cache[model_name] = model
    return model


def transcribe_audio(
    audio_path: str,
    model_name: str = "base",
    language: Optional[str] = None,
) -> dict:
    """
    Transcribe an audio file using OpenAI's Whisper model.

    Args:
        audio_path: Path to the audio file.
        model_name: Whisper model size (tiny, base, small, medium, large).
        language: Optional ISO-639-1 language code (e.g. ``"en"``).
                  If *None*, Whisper auto-detects the language.

    Returns:
        Whisper result dict containing ``text`` and ``segments``.

    Raises:
        ValueError: If the model name is invalid.
        FileNotFoundError: If the audio file does not exist.
    """
    if model_name not in VALID_MODELS:
        raise ValueError(
            f"Invalid model '{model_name}'. "
            f"Choose from: {', '.join(sorted(VALID_MODELS))}"
        )
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_model(model_name)

    log.info("Transcribing %s...", audio_path)

    kwargs: Dict[str, Any] = {}
    if language:
        kwargs["language"] = language

    result = model.transcribe(audio_path, **kwargs)
    return result
