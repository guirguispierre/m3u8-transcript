"""PDF transcript generation from Whisper segments."""

import logging
from datetime import timedelta
from typing import Any, Dict, List

from fpdf import FPDF

log = logging.getLogger(__name__)


class PDFTranscript(FPDF):
    """Custom FPDF subclass with header/footer for transcripts."""

    def header(self) -> None:
        self.set_font("helvetica", "B", 12)
        self.cell(
            0, 10, "Audio Transcript",
            border=False, new_x="LMARGIN", new_y="NEXT", align="C",
        )
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def format_seconds(seconds: float) -> str:
    """Convert a number of seconds to an ``HH:MM:SS`` string."""
    return str(timedelta(seconds=int(seconds)))


def create_pdf(
    segments: List[Dict[str, Any]],
    output_filename: str,
) -> None:
    """
    Generate a timestamped PDF transcript from Whisper segments.

    Args:
        segments: List of segment dicts with ``start``, ``end``, and ``text``.
        output_filename: Destination path for the PDF file.
    """
    if not segments:
        log.warning("No segments provided -- PDF will be empty.")

    pdf = PDFTranscript()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=10)

    for segment in segments:
        start = format_seconds(segment["start"])
        end = format_seconds(segment["end"])
        text = segment["text"].strip()

        # Timestamp in bold
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(
            30, 8, f"[{start} - {end}]",
            new_x="RIGHT", new_y="TOP", align="L",
        )

        # Text in regular
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 8, text)
        pdf.ln(2)

    log.info("Writing PDF to %s...", output_filename)
    pdf.output(output_filename)
    log.info("PDF generation complete.")
