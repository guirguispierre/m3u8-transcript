"""GUI application for the M3U8 Transcript Generator."""

import logging
import os
import threading

import customtkinter as ctk

from logger import setup_logging
from workflow import generate_transcript
from writers import SUPPORTED_FORMATS

# Initialise logging (GUI might be launched directly)
setup_logging()
log = logging.getLogger(__name__)

ctk.set_default_color_theme("blue")

# Accent colours
_ACCENT = "#3B8ED0"
_ACCENT_HOVER = "#2B7BBF"
_SUCCESS = "#2FA572"
_DANGER = "#D9534F"
_DANGER_HOVER = "#C9302C"
_MUTED = "#6B7280"


class TranscriptApp(ctk.CTk):
    """Main GUI window."""

    def __init__(self) -> None:
        super().__init__()

        self._cancel_event = threading.Event()

        # ── Window setup ─────────────────────────────────────────────
        self.title("M3U8 Transcript Generator")
        self.geometry("660x720")
        self.minsize(580, 660)
        self.grid_columnconfigure(0, weight=1)

        # Use system preference (Dark/Light) by default
        ctk.set_appearance_mode("System")

        row = 0

        # ── Title bar area ───────────────────────────────────────────
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=row, column=0, padx=20, pady=(18, 0), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_frame, text="M3U8 Transcript Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.appearance_toggle = ctk.CTkSegmentedButton(
            title_frame, values=["System", "Dark", "Light"],
            command=self._change_appearance,
            font=ctk.CTkFont(size=12),
        )
        self.appearance_toggle.set("System")
        self.appearance_toggle.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            title_frame,
            text="Download, transcribe, and export m3u8 streams in seconds.",
            font=ctk.CTkFont(size=13),
            text_color=_MUTED,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        row += 1

        # ── URL Input ────────────────────────────────────────────────
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=row, column=0, padx=20, pady=(14, 0), sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)
        row += 1

        ctk.CTkLabel(url_frame, text="Stream URL", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4),
        )
        self.url_entry = ctk.CTkEntry(
            url_frame, placeholder_text="https://example.com/stream/playlist.m3u8",
            height=38,
        )
        self.url_entry.grid(row=1, column=0, sticky="ew")

        # ── Options Card ─────────────────────────────────────────────
        self.options_card = ctk.CTkFrame(self, corner_radius=12)
        self.options_card.grid(row=row, column=0, padx=20, pady=(14, 0), sticky="ew")
        self.options_card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        row += 1

        # Row 0: Model + Format
        ctk.CTkLabel(
            self.options_card, text="Model", font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, padx=(14, 4), pady=(14, 2), sticky="w")

        self.model_menu = ctk.CTkOptionMenu(
            self.options_card,
            values=["tiny", "base", "small", "medium", "large"],
            height=32,
        )
        self.model_menu.set("base")
        self.model_menu.grid(row=0, column=1, padx=4, pady=(14, 2), sticky="ew")

        ctk.CTkLabel(
            self.options_card, text="Format", font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=2, padx=(14, 4), pady=(14, 2), sticky="w")

        self.format_menu = ctk.CTkOptionMenu(
            self.options_card,
            values=sorted(SUPPORTED_FORMATS),
            height=32,
        )
        self.format_menu.set("pdf")
        self.format_menu.grid(row=0, column=3, padx=(4, 14), pady=(14, 2), sticky="ew")

        # Row 1: Language + Keep Audio
        ctk.CTkLabel(
            self.options_card, text="Language", font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=1, column=0, padx=(14, 4), pady=(8, 2), sticky="w")

        self.language_entry = ctk.CTkEntry(
            self.options_card, placeholder_text="auto  (en, fr, es ...)",
            height=32,
        )
        self.language_entry.grid(row=1, column=1, padx=4, pady=(8, 2), sticky="ew")

        self.keep_audio_switch = ctk.CTkSwitch(
            self.options_card, text="Keep audio file",
            font=ctk.CTkFont(size=12),
        )
        self.keep_audio_switch.grid(
            row=1, column=2, columnspan=2, padx=14, pady=(8, 2), sticky="w",
        )

        # Row 2: Output path
        ctk.CTkLabel(
            self.options_card, text="Save to", font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=2, column=0, padx=(14, 4), pady=(8, 14), sticky="w")

        self.output_entry = ctk.CTkEntry(
            self.options_card,
            placeholder_text="transcripts/transcript_<timestamp>.<fmt>",
            height=32,
        )
        self.output_entry.grid(row=2, column=1, columnspan=2, padx=4, pady=(8, 14), sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.options_card, text="Browse",
            width=80, height=32,
            command=self._browse_output,
        )
        self.browse_button.grid(row=2, column=3, padx=(4, 14), pady=(8, 14), sticky="ew")

        # ── Action buttons ───────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=20, pady=(16, 0), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        row += 1

        self.generate_btn = ctk.CTkButton(
            btn_frame, text="Generate Transcript",
            height=42, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._start_generation,
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", width=90, height=42,
            fg_color=_MUTED, hover_color=_DANGER_HOVER,
            state="disabled",
            command=self._request_cancel,
        )
        self.cancel_btn.grid(row=0, column=1, padx=(10, 0))

        # ── Progress bar ─────────────────────────────────────────────
        self.progress_bar = ctk.CTkProgressBar(self, height=6, corner_radius=3)
        self.progress_bar.grid(row=row, column=0, padx=20, pady=(12, 0), sticky="ew")
        self.progress_bar.set(0)
        row += 1

        # ── Log / status box ────────────────────────────────────────
        log_label_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_label_frame.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="ew")
        row += 1

        ctk.CTkLabel(
            log_label_frame, text="Output Log",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=_MUTED,
        ).pack(anchor="w")

        self.log_box = ctk.CTkTextbox(
            self, height=120, corner_radius=10, font=ctk.CTkFont(size=12),
            state="disabled", wrap="word",
        )
        self.log_box.grid(row=row, column=0, padx=20, pady=(4, 0), sticky="nsew")
        self.grid_rowconfigure(row, weight=1)
        row += 1

        # ── Status bar ───────────────────────────────────────────────
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=row, column=0, padx=20, pady=(6, 10), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready", text_color=_MUTED,
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            status_frame, text="Made by Pierre Guirguis with love",
            font=ctk.CTkFont(size=11, slant="italic"), text_color=_MUTED,
        ).grid(row=0, column=1, sticky="e")

    # ------------------------------------------------------------------
    # Theme toggle
    # ------------------------------------------------------------------

    @staticmethod
    def _change_appearance(mode: str) -> None:
        ctk.set_appearance_mode(mode)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _browse_output(self) -> None:
        fmt = self.format_menu.get()
        ext = {"pdf": ".pdf", "srt": ".srt", "txt": ".txt"}.get(fmt, ".pdf")
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

    # ── Thread-safe UI updates ───────────────────────────────────────

    def _update_status(self, message: str, color: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=message, text_color=color))

    def _append_log(self, text: str) -> None:
        """Thread-safe log box append."""
        def _write() -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _write)

    def _set_progress(self, value: float) -> None:
        self.after(0, lambda: self.progress_bar.set(value))

    def _request_cancel(self) -> None:
        self._cancel_event.set()
        self._update_status("Cancelling...", "orange")
        self._append_log("[!] Cancel requested -- waiting for current step...")

    def _set_running(self, running: bool) -> None:
        def _apply() -> None:
            if running:
                self.generate_btn.configure(state="disabled")
                self.cancel_btn.configure(state="normal", fg_color=_DANGER, hover_color=_DANGER_HOVER)
            else:
                self.generate_btn.configure(state="normal")
                self.cancel_btn.configure(state="disabled", fg_color=_MUTED)
        self.after(0, _apply)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def _start_generation(self) -> None:
        url = self.url_entry.get().strip()
        if not url:
            self._update_status("Please enter a URL.", "red")
            return
        if not url.startswith(("http://", "https://")):
            self._update_status("Invalid URL -- must start with http:// or https://", "red")
            return

        # Clear log
        self.after(0, lambda: (
            self.log_box.configure(state="normal"),
            self.log_box.delete("1.0", "end"),
            self.log_box.configure(state="disabled"),
        ))

        self._cancel_event.clear()
        self._set_running(True)
        self._update_status("Starting...", _ACCENT)
        self._set_progress(0)

        threading.Thread(target=self._run, args=(url,), daemon=True).start()

    def _run(self, url: str) -> None:
        model = self.model_menu.get()
        keep = bool(self.keep_audio_switch.get())
        output = self.output_entry.get().strip() or None
        fmt = self.format_menu.get()
        lang = self.language_entry.get().strip() or None

        step = 0
        total = 3

        def on_status(msg: str) -> None:
            nonlocal step
            step += 1
            self._set_progress(min(step / total, 0.95))
            self._update_status(msg, "orange")
            self._append_log(f"[{step}/{total}] {msg}")

        try:
            if self._cancel_event.is_set():
                self._update_status("Cancelled.", _MUTED)
                self._append_log("[x] Cancelled before start.")
                return

            result_path = generate_transcript(
                url=url,
                model_name=model,
                output_path=output,
                keep_audio=keep,
                output_format=fmt,
                language=lang,
                on_status=on_status,
            )

            if self._cancel_event.is_set():
                self._update_status("Cancelled.", _MUTED)
                self._append_log("[x] Cancelled.")
                return

            self._set_progress(1.0)
            self._update_status(f"Done -- saved to {os.path.basename(result_path)}", _SUCCESS)
            self._append_log(f"[OK] Transcript saved to {result_path}")

        except Exception as exc:
            log.exception("Generation failed")
            self._update_status(f"Error: {exc}", "red")
            self._append_log(f"[ERROR] {exc}")

        finally:
            self._set_running(False)


if __name__ == "__main__":
    app = TranscriptApp()
    app.mainloop()
