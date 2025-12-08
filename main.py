import argparse
import os
from transcriber import download_audio, transcribe_audio
from pdf_writer import create_pdf

def main():
    parser = argparse.ArgumentParser(description="Convert m3u8 audio stream to PDF transcript.")
    parser.add_argument("url", help="The m3u8 URL to transcribe.")
    parser.add_argument("--output", "-o", help="Output PDF filename.", default="transcript.pdf")
    parser.add_argument("--model", "-m", help="Whisper model to use (tiny, base, small, medium, large).", default="base")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the downloaded audio file.")

    args = parser.parse_args()

    audio_filename = "temp_audio.mp3"

    try:
        # 1. Download
        download_audio(args.url, audio_filename)

        # 2. Transcribe
        result = transcribe_audio(audio_filename, model_name=args.model)
        
        # 3. Generate PDF
        create_pdf(result['segments'], args.output)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if not args.keep_audio and os.path.exists(audio_filename):
            os.remove(audio_filename)
            print(f"Removed temporary file {audio_filename}")

if __name__ == "__main__":
    main()
