import subprocess
import os
import tempfile
import whisper


VALID_MODELS = {"tiny", "base", "small", "medium", "large"}


def make_temp_audio_path() -> str:
    """Create a unique temporary file path for audio downloads."""
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    return path


def download_audio(m3u8_url: str, output_path: str) -> str:
    """
    Downloads audio from an m3u8 stream and saves it as an MP3 file using yt-dlp.

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
        raise ValueError(f"Invalid URL (must start with http:// or https://): {m3u8_url}")

    try:
        print(f"Downloading audio from {m3u8_url} using yt-dlp...")

        base_name = os.path.splitext(output_path)[0]

        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", f"{base_name}.%(ext)s",
            "--force-overwrites",
            "--no-check-certificates",
            m3u8_url
        ]

        subprocess.run(cmd, check=True)

        expected_file = f"{base_name}.mp3"
        if os.path.exists(expected_file):
            print(f"Audio saved to {expected_file}")
            return expected_file
        else:
            raise FileNotFoundError(f"yt-dlp finished but {expected_file} was not found.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading audio with yt-dlp: {e}")
        raise


def transcribe_audio(audio_path: str, model_name: str = "base") -> dict:
    """
    Transcribes an audio file using OpenAI's Whisper model.

    Args:
        audio_path: Path to the audio file.
        model_name: Whisper model size (tiny, base, small, medium, large).

    Returns:
        Whisper result dict containing 'text' and 'segments'.

    Raises:
        ValueError: If the model name is invalid.
        FileNotFoundError: If the audio file does not exist.
    """
    if model_name not in VALID_MODELS:
        raise ValueError(
            f"Invalid model '{model_name}'. Choose from: {', '.join(sorted(VALID_MODELS))}"
        )
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)

    return result
