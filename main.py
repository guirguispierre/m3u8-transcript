"""CLI entry point for the M3U8 Transcript Generator."""

import argparse
import logging
import sys

from logger import setup_logging
from transcriber import VALID_MODELS
from workflow import generate_transcript
from writers import SUPPORTED_FORMATS

log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert m3u8 audio stream to a transcript (PDF, SRT, or TXT).",
    )
    parser.add_argument("url", nargs="?", help="The m3u8 URL to transcribe.")
    parser.add_argument(
        "--output", "-o",
        help="Output filename. If not specified, saves to 'transcripts/' with a timestamp.",
        default=None,
    )
    parser.add_argument(
        "--format", "-f",
        help="Output format (default: pdf).",
        default="pdf",
        choices=sorted(SUPPORTED_FORMATS),
        dest="fmt",
    )
    parser.add_argument(
        "--model", "-m",
        help="Whisper model to use (tiny, base, small, medium, large).",
        default="base",
        choices=sorted(VALID_MODELS),
    )
    parser.add_argument(
        "--language", "-l",
        help="ISO-639-1 language code (e.g. 'en', 'fr'). Auto-detects if omitted.",
        default=None,
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded audio file.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the GUI interface.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging.",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=level)

    # Launch GUI if no URL provided OR --gui flag is set
    if args.gui or not args.url:
        log.info("Launching GUI...")
        from gui import TranscriptApp
        app = TranscriptApp()
        app.mainloop()
        return

    # CLI Mode
    try:
        output = generate_transcript(
            url=args.url,
            model_name=args.model,
            output_path=args.output,
            keep_audio=args.keep_audio,
            output_format=args.fmt,
            language=args.language,
        )
        log.info("Done! Transcript saved to: %s", output)

    except Exception:
        log.exception("Transcript generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
