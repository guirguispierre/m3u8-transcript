# m3u8 to PDF Transcript

A Python tool that downloads audio from an m3u8 stream (including complex Mediasite streams), transcribes it using [OpenAI Whisper](https://github.com/openai/whisper), and generates a clean PDF transcript with timestamps.

## Features
- **Robust Downloading**: Uses `yt-dlp` to handle complex HLS streams and authentication tokens.
- **Accurate Transcription**: Uses OpenAI's Whisper model (runs locally).
- **PDF Output**: Generates readable PDFs with timestamps.

## Prerequisites
- Python 3.9+
- [FFmpeg](https://ffmpeg.org/download.html) installed and on your system PATH.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/guirguispierre/m3u8-transcript.git
   cd m3u8-transcript
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python3 main.py "YOUR_M3U8_URL"
```

### Finding the URL for Mediasite/Protected Videos
If you are trying to transcribe a protected video (e.g., from a university lecture portal), you cannot use the page URL. You must find the **Manifest URL**.

1. Open the video page in your browser.
2. Open Developer Tools (F12 or Right Click -> Inspect).
3. Go to the **Network** tab.
4. Filter by `manifest`.
5. Reload the page and play the video.
6. Look for a request ending in `manifest(...)` or `.ism`.
   - It usually has a query parameter like `?playbackTicket=...`.
7. Right-click -> Copy Link Address.
8. Paste that URL into the tool.

### Options

- `-o`, `--output`: Specify output filename (default: `transcript.pdf`)
  ```bash
  python3 main.py "URL" -o my_lecture.pdf
  ```
- `-m`, `--model`: Specify Whisper model size (`tiny`, `base`, `small`, `medium`, `large`). Default is `base`.
  ```bash
  python3 main.py "URL" -m medium
  ```
- `--keep-audio`: Keep the downloaded MP3 file after transcription.
  ```bash
  python3 main.py "URL" --keep-audio
  ```
