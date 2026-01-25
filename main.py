import argparse
import os
from datetime import datetime
from transcriber import download_audio, transcribe_audio
from pdf_writer import create_pdf

TRANSCRIPTS_DIR = "transcripts"

def main():
    parser = argparse.ArgumentParser(description="Convert m3u8 audio stream to PDF transcript.")
    parser.add_argument("url", nargs="?", help="The m3u8 URL to transcribe.")
    parser.add_argument("--output", "-o", help="Output PDF filename. If not specified, saves to 'transcripts/' with a timestamp.", default=None)
    parser.add_argument("--model", "-m", help="Whisper model to use (tiny, base, small, medium, large).", default="base")
    parser.add_argument("--keep-audio", action="store_true", help="Keep the downloaded audio file.")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI interface.")

    args = parser.parse_args()

    # Launch GUI if no URL provided OR --gui flag is set
    if args.gui or not args.url:
        print("Launching GUI...")
        from gui import TranscriptApp
        app = TranscriptApp()
        app.mainloop()
        return

    # CLI Mode
    if args.output:
        output_filename = args.output
    else:
        # Create transcripts directory if it doesn't exist
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(TRANSCRIPTS_DIR, f"transcript_{timestamp}.pdf")

    audio_filename = "temp_audio.mp3"

    try:
        # 1. Download
        download_audio(args.url, audio_filename)

        # 2. Transcribe
        result = transcribe_audio(audio_filename, model_name=args.model)
        
        # 3. Generate PDF
        create_pdf(result['segments'], output_filename)
        print(f"Transcript saved to: {output_filename}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if not args.keep_audio and os.path.exists(audio_filename):
            os.remove(audio_filename)
            print(f"Removed temporary file {audio_filename}")

if __name__ == "__main__":
    main()
