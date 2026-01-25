# M3U8 Transcript Generator Help

This tool downloads an audio stream from an m3u8 URL, transcribes it using OpenAI's Whisper, and saves the transcript as a PDF.

## Usage

### Basic Command
Run the script with the m3u8 URL:

```bash
python3 main.py "YOUR_M3U8_URL_HERE"
```

### Launch GUI
To open the graphical interface:
```bash
python3 main.py --gui
```
*Or simply run `python3 main.py` without arguments.*

### Options

| Argument | Description | Default |
| :--- | :--- | :--- |
| `url` | The URL of the m3u8 stream. Optional if using GUI. | N/A |
| `--gui` | Launch the Graphical User Interface. | `False` |
| `-o`, `--output` | Specify a custom filename/path for the PDF. | `transcripts/transcript_<timestamp>.pdf` |
| `-m`, `--model` | specific Whisper model to use. Options: `tiny`, `base`, `small`, `medium`, `large`. | `base` |
| `--keep-audio` | Keep the temporary `.mp3` file after processing. | `False` (deletes audio) |

### Examples

**1. Default run (Recommended):**
```bash
python3 main.py "https://example.com/video.m3u8"
```
*Saves to `transcripts/` folder.*

**2. Specify a custom output filename:**
```bash
python3 main.py "https://example.com/video.m3u8" -o "my_lecture_notes.pdf"
```

**3. Use a more accurate model (slower):**
```bash
python3 main.py "https://example.com/video.m3u8" --model medium
```

**4. Keep the audio file for later use:**
```bash
python3 main.py "https://example.com/video.m3u8" --keep-audio
```

## Setup & Requirements

Ensure you have the required dependencies installed:
```bash
pip install -r requirements.txt
pip install --upgrade llvmlite numba
```
You also need `ffmpeg` installed on your system (e.g., `brew install ffmpeg`).
