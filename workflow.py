"""
Shared transcript generation workflow.

Centralises the download -> transcribe -> write pipeline so that both
the CLI (main.py) and the GUI (gui.py) call the same logic.
"""

import logging
import os
from datetime import datetime
from typing import Callable, Optional

from transcriber import download_audio, transcribe_audio, make_temp_audio_path
from writers import write_transcript, SUPPORTED_FORMATS

log = logging.getLogger(__name__)

TRANSCRIPTS_DIR = "transcripts"

# File-extension map for each supported format
_FORMAT_EXT = {
    "pdf": ".pdf",
    "srt": ".srt",
    "txt": ".txt",
}


def resolve_output_path(
    custom_output: Optional[str] = None,
    fmt: str = "pdf",
) -> str:
    """
    Determine the final output file path.

    If *custom_output* is provided (and non-empty), use it and ensure its
    parent directory exists.  Otherwise, generate a timestamped path inside
    ``transcripts/``.
    """
    if custom_output and custom_output.strip():
        output = custom_output.strip()
        parent = os.path.dirname(output)
        if parent:
            os.makedirs(parent, exist_ok=True)
        return output

    ext = _FORMAT_EXT.get(fmt, ".pdf")
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(TRANSCRIPTS_DIR, f"transcript_{timestamp}{ext}")


def generate_transcript(
    url: str,
    model_name: str = "base",
    output_path: Optional[str] = None,
    keep_audio: bool = False,
    output_format: str = "pdf",
    language: Optional[str] = None,
    on_status: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Full pipeline: download audio, transcribe with Whisper, write output.

    Args:
        url: M3U8 / stream URL.
        model_name: Whisper model size.
        output_path: Custom output path (None for auto-generated).
        keep_audio: If True, keep the temporary MP3 after finishing.
        output_format: Output format -- ``pdf``, ``srt``, or ``txt``.
        language: Optional ISO-639-1 language code for Whisper.
        on_status: Optional callback invoked with status messages.

    Returns:
        The path to the generated transcript file.

    Raises:
        ValueError, FileNotFoundError, subprocess.CalledProcessError, etc.
    """

    def _status(msg: str) -> None:
        log.info(msg)
        if on_status:
            on_status(msg)

    audio_path = make_temp_audio_path()
    output = resolve_output_path(output_path, fmt=output_format)

    try:
        # 1. Download
        _status("Downloading audio...")
        download_audio(url, audio_path)

        # 2. Transcribe
        _status(f"Transcribing with '{model_name}' model...")
        result = transcribe_audio(audio_path, model_name=model_name, language=language)

        # 3. Write output
        _status(f"Writing {output_format.upper()} transcript...")
        metadata = {
            "source_url": url,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": model_name,
            "language": language or "auto-detected",
        }
        write_transcript(output_format, result["segments"], output, metadata=metadata)
        _status(f"Transcript saved to: {output}")

        return output

    finally:
        # Cleanup temp audio
        if not keep_audio and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                log.debug("Removed temporary file %s", audio_path)
            except OSError as exc:
                log.warning("Failed to remove temp file %s: %s", audio_path, exc)
