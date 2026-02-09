"""
Output format writers for transcript segments.

Supported formats: PDF, SRT, TXT.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fpdf import FPDF

log = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"pdf", "srt", "txt"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_seconds(seconds: float) -> str:
    """Convert seconds to ``HH:MM:SS``."""
    return str(timedelta(seconds=int(seconds)))


def _srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp ``HH:MM:SS,mmm``."""
    td = timedelta(seconds=seconds)
    total_secs = int(td.total_seconds())
    hours, remainder = divmod(total_secs, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# ---------------------------------------------------------------------------
# PDF writer
# ---------------------------------------------------------------------------

class PDFTranscript(FPDF):
    """FPDF subclass with transcript header/footer."""

    def __init__(self, metadata: Optional[Dict[str, str]] = None) -> None:
        super().__init__()
        self._meta = metadata or {}

    def header(self) -> None:
        self.set_font("helvetica", "B", 14)
        self.cell(
            0, 10, "Audio Transcript",
            border=False, new_x="LMARGIN", new_y="NEXT", align="C",
        )

        # Metadata line (source, date, model)
        parts: List[str] = []
        if self._meta.get("date"):
            parts.append(f"Date: {self._meta['date']}")
        if self._meta.get("model"):
            parts.append(f"Model: {self._meta['model']}")
        if self._meta.get("language"):
            parts.append(f"Language: {self._meta['language']}")

        if parts:
            self.set_font("helvetica", "I", 8)
            self.cell(0, 6, "  |  ".join(parts), new_x="LMARGIN", new_y="NEXT", align="C")

        if self._meta.get("source_url"):
            self.set_font("helvetica", "I", 7)
            self.cell(
                0, 5, f"Source: {self._meta['source_url']}",
                new_x="LMARGIN", new_y="NEXT", align="C",
            )

        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def write_pdf(
    segments: List[Dict[str, Any]],
    output_path: str,
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """Write segments to a timestamped PDF."""
    if not segments:
        log.warning("No segments provided -- PDF will be empty.")

    pdf = PDFTranscript(metadata=metadata)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=10)

    for segment in segments:
        start = format_seconds(segment["start"])
        end = format_seconds(segment["end"])
        text = segment["text"].strip()

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 8, f"[{start} - {end}]", new_x="RIGHT", new_y="TOP", align="L")

        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 8, text)
        pdf.ln(2)

    log.info("Writing PDF to %s...", output_path)
    pdf.output(output_path)


# ---------------------------------------------------------------------------
# SRT writer
# ---------------------------------------------------------------------------

def write_srt(
    segments: List[Dict[str, Any]],
    output_path: str,
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """Write segments to an SRT subtitle file."""
    log.info("Writing SRT to %s...", output_path)
    with open(output_path, "w", encoding="utf-8") as fh:
        for idx, seg in enumerate(segments, start=1):
            start_ts = _srt_timestamp(seg["start"])
            end_ts = _srt_timestamp(seg["end"])
            text = seg["text"].strip()
            fh.write(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n\n")


# ---------------------------------------------------------------------------
# TXT writer
# ---------------------------------------------------------------------------

def write_txt(
    segments: List[Dict[str, Any]],
    output_path: str,
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """Write segments to a plain-text file with timestamps."""
    log.info("Writing TXT to %s...", output_path)
    with open(output_path, "w", encoding="utf-8") as fh:
        if metadata:
            if metadata.get("source_url"):
                fh.write(f"Source: {metadata['source_url']}\n")
            if metadata.get("date"):
                fh.write(f"Date:   {metadata['date']}\n")
            if metadata.get("model"):
                fh.write(f"Model:  {metadata['model']}\n")
            fh.write("\n" + "=" * 60 + "\n\n")

        for seg in segments:
            start = format_seconds(seg["start"])
            end = format_seconds(seg["end"])
            text = seg["text"].strip()
            fh.write(f"[{start} - {end}]  {text}\n")


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_WRITERS = {
    "pdf": write_pdf,
    "srt": write_srt,
    "txt": write_txt,
}


def write_transcript(
    fmt: str,
    segments: List[Dict[str, Any]],
    output_path: str,
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """
    Dispatch to the correct writer based on *fmt*.

    Args:
        fmt: Output format (``pdf``, ``srt``, or ``txt``).
        segments: Whisper segment dicts.
        output_path: Destination file path.
        metadata: Optional metadata dict for the header/footer.

    Raises:
        ValueError: If *fmt* is not supported.
    """
    fmt = fmt.lower()
    writer = _WRITERS.get(fmt)
    if writer is None:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )
    writer(segments, output_path, metadata)
    log.info("Transcript written to %s", output_path)
