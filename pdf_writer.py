"""
Backward-compatible PDF writer.

This module re-exports ``create_pdf`` and ``format_seconds`` from
:mod:`writers` so that existing code continues to work.
"""

from writers import format_seconds, write_pdf

__all__ = ["create_pdf", "format_seconds"]


def create_pdf(segments, output_filename):
    """Thin wrapper around :func:`writers.write_pdf` for backward compatibility."""
    write_pdf(segments, output_filename)
