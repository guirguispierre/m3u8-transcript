# CLAUDE.md

Guidelines for AI assistants working on the m3u8-transcript codebase.

## Project Overview

**m3u8-transcript** is a Python CLI/GUI tool that converts audio from m3u8 (HLS) streams into timestamped transcripts. The pipeline is: download audio via yt-dlp → transcribe with OpenAI Whisper (local, offline) → export to PDF, SRT, or TXT.

**Version**: 1.3.0
**License**: MIT
**Python**: 3.9+
**System requirement**: FFmpeg must be on PATH

## Architecture

```
User Input (main.py CLI / gui.py GUI)
    ↓
Workflow Pipeline (workflow.py)
    ├→ Download audio   (transcriber.py → yt-dlp)
    ├→ Transcribe        (transcriber.py → Whisper)
    └→ Write output      (writers.py → PDF/SRT/TXT)
```

### Module Responsibilities

| Module | Role |
|---|---|
| `main.py` | CLI entry point, argparse, launches GUI or CLI pipeline |
| `gui.py` | CustomTkinter GUI with threaded background processing |
| `workflow.py` | Orchestrates download → transcribe → write; shared by CLI and GUI |
| `transcriber.py` | Audio download (yt-dlp) and Whisper transcription with model caching |
| `writers.py` | Format writers (PDF via fpdf2, SRT, TXT) and dispatcher |
| `pdf_writer.py` | Backward-compatible wrapper re-exporting `create_pdf` / `format_seconds` |
| `logger.py` | Centralized logging setup (console + optional file) |
| `test_pdf_gen.py` | pytest test suite |

### Key Data Structures

Whisper segments (passed between modules):
```python
[{"start": float, "end": float, "text": str}, ...]
```

Metadata dict (passed to writers):
```python
{"source_url": str, "date": str, "model": str, "language": str}
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install in editable/dev mode
pip install -e ".[dev]"

# Run tests
pytest -v

# Run the app (GUI mode, default)
python3 main.py

# Run the app (CLI mode)
python3 main.py <M3U8_URL> --model base --format pdf

# Run with verbose logging
python3 main.py <URL> --verbose
```

## Testing

- Framework: **pytest**
- Test file: `test_pdf_gen.py` at project root
- Config: `pyproject.toml` under `[tool.pytest.ini_options]` (testpaths = `["."]`, pattern = `test_*.py`)
- Tests use `tmp_path` fixture for file I/O; no network calls needed
- Run: `pytest -v`

Test classes cover: time formatting, PDF/SRT/TXT generation, format dispatcher, model validation, and URL validation.

## Code Conventions

- **Type hints** on all function signatures
- **Google-style docstrings** on public functions
- **Snake_case** for functions/variables, **CamelCase** for classes, **UPPERCASE** for module constants
- **Private functions** prefixed with underscore (e.g., `_load_model`, `_status`)
- **Logging** via `log = logging.getLogger(__name__)` per module — never use `print()`
- **Error handling**: raise specific exceptions (`ValueError`, `FileNotFoundError`, `CalledProcessError`) with descriptive messages
- **Dispatcher pattern** in `writers.py`: dict-based format → function lookup
- **Module-level caching** for Whisper models (`_model_cache` dict in `transcriber.py`)
- **Thread safety**: GUI uses daemon threads + `widget.after()` for UI updates
- **Section dividers**: use `# ─── Section ───` comment style

## File Structure

```
m3u8-transcript/
├── main.py              # CLI entry point
├── gui.py               # CustomTkinter GUI
├── workflow.py          # Shared pipeline orchestration
├── transcriber.py       # yt-dlp download + Whisper transcription
├── writers.py           # PDF/SRT/TXT writers + dispatcher
├── pdf_writer.py        # Backward-compat wrapper
├── logger.py            # Logging config
├── test_pdf_gen.py      # Test suite
├── pyproject.toml       # Project metadata, deps, pytest config
├── requirements.txt     # Pinned dependencies
├── README.md            # User documentation
├── help.md              # CLI help reference
├── assets/              # Images (header.png, gui_dark.png)
├── transcripts/         # Auto-created output directory (gitignored)
└── .gitignore
```

## Dependencies

**Core**: openai-whisper, yt-dlp, ffmpeg-python, fpdf2, customtkinter, packaging, torch
**Dev**: pytest

All versions pinned in both `pyproject.toml` and `requirements.txt`.

## Common Patterns

- Both CLI and GUI delegate to `workflow.generate_transcript()` — changes to the pipeline only need to happen in `workflow.py`
- New output formats: add a writer function to `writers.py`, register it in `_WRITERS` dict, and add the key to `SUPPORTED_FORMATS`
- Progress reporting: pass an `on_status` callback to `generate_transcript()`
- Output paths: `workflow.resolve_output_path()` handles auto-timestamped naming into `transcripts/`
- `pdf_writer.py` exists solely for backward compatibility; new code should import from `writers` directly

## Things to Watch Out For

- The `transcripts/` directory and `*.pdf`/`*.mp3` files are gitignored — don't commit generated output
- Tests don't require Whisper model downloads or network access; they test writers and validation only
- The GUI lazily imports in `main.py` (inside the `if` branch) to avoid loading CustomTkinter when running in CLI mode
- `--no-check-certificates` is used in yt-dlp calls — this is intentional for HLS stream compatibility
