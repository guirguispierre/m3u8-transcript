import subprocess
import os
import whisper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def download_audio(m3u8_url, output_path):
    """
    Downloads audio from an m3u8 stream and saves it as an MP3 file using yt-dlp.
    """
    try:
        print(f"Downloading audio from {m3u8_url} using yt-dlp...")
        
        # yt-dlp adds extension automatically if we use a template or -o with extension
        # We want to force the final filename to be output_path
        # If output_path is 'temp_audio.mp3', we can pass -o 'temp_audio.%(ext)s' and ensure we ask for mp3
        
        base_name = os.path.splitext(output_path)[0]
        
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", f"{base_name}.%(ext)s",
            "--force-overwrites",
            m3u8_url
        ]
        
        subprocess.run(cmd, check=True)
        
        # Verify the file exists. yt-dlp should have created {base_name}.mp3
        expected_file = f"{base_name}.mp3"
        if os.path.exists(expected_file):
             # If we intended a specific full path and it matches, great. If not, we might need to rename.
             # In our main.py we pass "temp_audio.mp3". yt-dlp will make "temp_audio.mp3".
             print(f"Audio saved to {expected_file}")
             return expected_file
        else:
            raise FileNotFoundError(f"yt-dlp finished but {expected_file} was not found.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading audio with yt-dlp: {e}")
        raise

def transcribe_audio(audio_path, model_name='base'):
    """
    Transcribes audio file using OpenAI's Whisper model.
    """
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)
    
    return result
