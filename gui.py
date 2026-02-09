"""GUI application for the M3U8 Transcript Generator."""

import logging
import threading

import customtkinter as ctk

from logger import setup_logging
from workflow import generate_transcript
from writers import SUPPORTED_FORMATS

# Initialise logging (GUI might be launched directly)
setup_logging()
log = logging.getLogger(__name__)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TranscriptApp(ctk.CTk):
    """Main GUI window."""

    def __init__(self) -> None:
        super().__init__()

        self._cancel_event = threading.Event()

        self.title("M3U8 Transcript Generator")
        self.geometry("620x600")
        self.minsize(520, 550)

        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Header
        self.header_label = ctk.CTkLabel(
            self, text="M3U8 Transcript Generator",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.header_label.grid(row=row, column=0, padx=20, pady=(20, 10))
        row += 1

        # URL Input
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter M3U8 URL")
        self.url_entry.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        row += 1

        # ---- Options Frame ----
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        # Model Selection
        ctk.CTkLabel(self.options_frame, text="Model:").grid(
            row=0, column=0, padx=(10, 2), pady=10, sticky="w",
        )
        self.model_option_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["tiny", "base", "small", "medium", "large"],
        )
        self.model_option_menu.set("base")
        self.model_option_menu.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Format Selection
        ctk.CTkLabel(self.options_frame, text="Format:").grid(
            row=0, column=2, padx=(10, 2), pady=10, sticky="w",
        )
        self.format_option_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=sorted(SUPPORTED_FORMATS),
        )
        self.format_option_menu.set("pdf")
        self.format_option_menu.grid(row=0, column=3, padx=(5, 10), pady=10, sticky="ew")

        # Language Input
        ctk.CTkLabel(self.options_frame, text="Language:").grid(
            row=1, column=0, padx=(10, 2), pady=10, sticky="w",
        )
        self.language_entry = ctk.CTkEntry(
            self.options_frame,
            placeholder_text="auto (e.g. en, fr, es)",
            width=120,
        )
        self.language_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Keep Audio Checkbox
        self.keep_audio_checkbox = ctk.CTkCheckBox(
            self.options_frame, text="Keep Audio File",
        )
        self.keep_audio_checkbox.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

        # ---- Output File Selection ----
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        row += 1

        self.output_entry = ctk.CTkEntry(
            self.output_frame,
            placeholder_text="Default: transcripts/transcript_<timestamp>.<fmt>",
        )
        self.output_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.output_frame, text="Save As...", width=100,
            command=self.browse_output_file,
        )
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)

        # ---- Progress Bar ----
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=row, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)
        row += 1

        # ---- Buttons Frame ----
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=row, column=0, padx=20, pady=10)
        row += 1

        self.generate_button = ctk.CTkButton(
            self.buttons_frame, text="Generate Transcript",
            command=self.start_generation_thread,
        )
        self.generate_button.grid(row=0, column=0, padx=10)

        self.cancel_button = ctk.CTkButton(
            self.buttons_frame, text="Cancel",
            command=self._request_cancel,
            state="disabled",
            fg_color="gray",
        )
        self.cancel_button.grid(row=0, column=1, padx=10)

        # ---- Status Label ----
        self.status_label = ctk.CTkLabel(self, text="Ready", text_color="gray")
        self.status_label.grid(row=row, column=0, padx=20, pady=(0, 10))
        row += 1

        # ---- Footer ----
        self.footer_label = ctk.CTkLabel(
            self, text="Made by Pierre Guirguis with love",
            font=ctk.CTkFont(size=12, slant="italic"),
        )
        self.footer_label.grid(row=row, column=0, padx=20, pady=10, sticky="s")
        self.grid_rowconfigure(row, weight=1)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def browse_output_file(self) -> None:
        fmt = self.format_option_menu.get()
        ext_map = {"pdf": ".pdf", "srt": ".srt", "txt": ".txt"}
        ext = ext_map.get(fmt, ".pdf")
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[
                ("PDF files", "*.pdf"),
                ("SRT subtitles", "*.srt"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, filename)

    def update_status(self, message: str, color: str) -> None:
        """Thread-safe status update."""
        self.after(
            0,
            lambda: self.status_label.configure(text=message, text_color=color),
        )

    def _set_progress(self, value: float) -> None:
        """Thread-safe progress bar update (0.0 - 1.0)."""
        self.after(0, lambda: self.progress_bar.set(value))

    def _request_cancel(self) -> None:
        """Signal the background thread to stop."""
        self._cancel_event.set()
        self.update_status("Cancelling...", "orange")

    def _set_running(self, running: bool) -> None:
        """Toggle button states between running / idle."""
        def _apply() -> None:
            if running:
                self.generate_button.configure(state="disabled")
                self.cancel_button.configure(state="normal", fg_color="#d9534f")
            else:
                self.generate_button.configure(state="normal")
                self.cancel_button.configure(state="disabled", fg_color="gray")
        self.after(0, _apply)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def start_generation_thread(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Please enter a URL.", "red")
            return

        if not url.startswith(("http://", "https://")):
            self.update_status("Invalid URL. Must start with http:// or https://", "red")
            return

        self._cancel_event.clear()
        self._set_running(True)
        self.update_status("Starting...", "blue")
        self._set_progress(0)

        thread = threading.Thread(
            target=self._run_generation, args=(url,), daemon=True,
        )
        thread.start()

    def _run_generation(self, url: str) -> None:
        """Background worker -- calls the shared workflow."""
        model_name = self.model_option_menu.get()
        keep_audio = bool(self.keep_audio_checkbox.get())
        custom_output = self.output_entry.get().strip() or None
        output_format = self.format_option_menu.get()
        language = self.language_entry.get().strip() or None

        step = 0
        total_steps = 3  # download, transcribe, write

        def on_status(msg: str) -> None:
            nonlocal step
            step += 1
            self._set_progress(min(step / total_steps, 0.95))
            self.update_status(msg, "orange")

        try:
            if self._cancel_event.is_set():
                self.update_status("Cancelled.", "gray")
                return

            output = generate_transcript(
                url=url,
                model_name=model_name,
                output_path=custom_output,
                keep_audio=keep_audio,
                output_format=output_format,
                language=language,
                on_status=on_status,
            )

            if self._cancel_event.is_set():
                self.update_status("Cancelled.", "gray")
                return

            self._set_progress(1.0)
            self.update_status(f"Success! Saved to {output}", "green")

        except Exception as exc:
            log.exception("Generation failed")
            self.update_status(f"Error: {exc}", "red")

        finally:
            self._set_running(False)


if __name__ == "__main__":
    app = TranscriptApp()
    app.mainloop()
