import customtkinter as ctk
import threading
import os
from datetime import datetime

from transcriber import download_audio, transcribe_audio, make_temp_audio_path
from pdf_writer import create_pdf

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

TRANSCRIPTS_DIR = "transcripts"


class TranscriptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("M3U8 Transcript Generator")
        self.geometry("600x500")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=0)

        # Header
        self.header_label = ctk.CTkLabel(
            self, text="M3U8 Transcript Generator",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # URL Input
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter M3U8 URL")
        self.url_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Options Frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1), weight=1)

        # Model Selection
        self.model_label = ctk.CTkLabel(self.options_frame, text="Whisper Model:")
        self.model_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.model_option_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["tiny", "base", "small", "medium", "large"],
        )
        self.model_option_menu.set("base")
        self.model_option_menu.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Keep Audio Checkbox
        self.keep_audio_checkbox = ctk.CTkCheckBox(self.options_frame, text="Keep Audio File")
        self.keep_audio_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Output File Selection
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            self.output_frame,
            placeholder_text="Default: transcripts/transcript_<timestamp>.pdf",
        )
        self.output_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.output_frame, text="Save As...", width=100,
            command=self.browse_output_file,
        )
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # Generate Button
        self.generate_button = ctk.CTkButton(
            self, text="Generate Transcript",
            command=self.start_generation_thread,
        )
        self.generate_button.grid(row=4, column=0, padx=20, pady=20)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=(0, 20))

        # Footer
        self.footer_label = ctk.CTkLabel(
            self, text="Made by Pierre Guirguis with love",
            font=ctk.CTkFont(size=12, slant="italic"),
        )
        self.footer_label.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        self.grid_rowconfigure(6, weight=1)

    def browse_output_file(self):
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if filename:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, filename)

    def start_generation_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Please enter a URL.", "red")
            return

        if not url.startswith(("http://", "https://")):
            self.update_status("Invalid URL. Must start with http:// or https://", "red")
            return

        self.generate_button.configure(state="disabled")
        self.update_status("Starting...", "blue")

        thread = threading.Thread(target=self.generate_transcript, args=(url,), daemon=True)
        thread.start()

    def generate_transcript(self, url: str):
        model_name = self.model_option_menu.get()
        keep_audio = self.keep_audio_checkbox.get()
        custom_output = self.output_entry.get().strip()
        audio_filename = make_temp_audio_path()

        try:
            # 1. Download
            self.update_status("Downloading audio...", "orange")
            download_audio(url, audio_filename)

            # 2. Transcribe
            self.update_status(f"Transcribing with '{model_name}' model...", "orange")
            result = transcribe_audio(audio_filename, model_name=model_name)

            # 3. Generate PDF
            if custom_output:
                output_filename = custom_output
                output_dir = os.path.dirname(output_filename)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
            else:
                os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_filename = os.path.join(TRANSCRIPTS_DIR, f"transcript_{timestamp}.pdf")

            self.update_status("Generating PDF...", "orange")
            create_pdf(result["segments"], output_filename)

            self.update_status(f"Success! Saved to {output_filename}", "green")

        except Exception as e:
            self.update_status(f"Error: {e}", "red")
        finally:
            if not keep_audio and os.path.exists(audio_filename):
                try:
                    os.remove(audio_filename)
                except OSError as cleanup_error:
                    print(f"Failed to remove temp file: {cleanup_error}")

            # Re-enable button on the main thread
            self.after(0, lambda: self.generate_button.configure(state="normal"))

    def update_status(self, message: str, color: str):
        """Thread-safe status update -- schedules the change on the main thread."""
        self.after(0, lambda: self.status_label.configure(text=message, text_color=color))


if __name__ == "__main__":
    app = TranscriptApp()
    app.mainloop()
