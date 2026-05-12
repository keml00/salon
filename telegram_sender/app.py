"""
Telegram Salon Messenger — Desktop GUI App
by keml00, Telegram

Modern GUI for sending Telegram messages without saving contacts.
Uses CustomTkinter for beautiful cross-platform interface.
"""

import customtkinter as ctk
import asyncio
import threading
from tkinter import filedialog, messagebox
import telegram_client
import ai_formatter
import history


# ============================================================
# THEME & COLORS
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Custom color palette
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_card": "#16213e",
    "accent": "#0f3460",
    "primary": "#e94560",
    "success": "#00d2d3",
    "warning": "#feca57",
    "text": "#ffffff",
    "text_muted": "#a0a0b0",
}


# ============================================================
# ASYNC HELPER — run async code from tkinter mainloop
# ============================================================
def run_async(coro):
    """Run async coroutine in a background thread."""
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    return _run


# ============================================================
# MAIN APPLICATION
# ============================================================
class TelegramSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("✈️ Telegram Salon Messenger")
        self.geometry("750x680")
        self.minsize(650, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        self._build_ui()

    def _build_ui(self):
        """Build all UI components."""

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="✈️  Telegram Salon Messenger",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["primary"],
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            header,
            text="Отправляй сообщения клиентам без сохранения номера",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, 10))

        # --- Recipient input ---
        input_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        input_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            input_frame,
            text="📱 Получатель (номер или @username):",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=15, pady=(10, 3))

        self.recipient_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="+79991234567 или @username",
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=8,
        )
        self.recipient_entry.pack(fill="x", padx=15, pady=(0, 12))

        # --- Message input ---
        msg_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(
            msg_frame,
            text="💬 Сообщение:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=15, pady=(10, 3))

        self.message_textbox = ctk.CTkTextbox(
            msg_frame,
            height=140,
            font=ctk.CTkFont(size=13),
            corner_radius=8,
            fg_color="#0d1b2a",
        )
        self.message_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        # --- Action buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=8)

        self.send_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Отправить",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color="#c73e54",
            height=42,
            corner_radius=10,
            command=self._on_send,
        )
        self.send_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.format_btn = ctk.CTkButton(
            btn_frame,
            text="✨ Форматировать AI",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#00b8b8",
            text_color="#000000",
            height=42,
            corner_radius=10,
            command=self._on_format,
        )
        self.format_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.history_btn = ctk.CTkButton(
            btn_frame,
            text="📋 История",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color="#0a2540",
            height=42,
            corner_radius=10,
            command=self._on_history,
        )
        self.history_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # --- Status bar ---
        self.status_label = ctk.CTkLabel(
            self,
            text="Готово к отправке",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(pady=(5, 2))

        # --- Footer ---
        ctk.CTkLabel(
            self,
            text="by keml00, Telegram",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, 10))

    # ============================================================
    # HANDLERS
    # ============================================================

    def _set_status(self, text: str, color: str = None):
        """Update status label."""
        self.status_label.configure(text=text)
        if color:
            self.status_label.configure(text_color=color)

    def _on_send(self):
        """Handle send button click."""
        recipient = self.recipient_entry.get().strip()
        text = self.message_textbox.get("1.0", "end").strip()

        # Validation
        if not recipient:
            self._set_status("❌ Укажите получателя!", COLORS["primary"])
            return
        if not text:
            self._set_status("❌ Введите сообщение!", COLORS["primary"])
            return

        self._set_status("⏳ Отправка...", COLORS["warning"])
        self.send_btn.configure(state="disabled")

        def _send_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                telegram_client.send_message(recipient, text)
            )
            loop.close()

            # Update UI from main thread
            self.after(0, lambda: self._on_send_result(result, recipient, text))

        threading.Thread(target=_send_task, daemon=True).start()

    def _on_send_result(self, result: dict, recipient: str, text: str):
        """Handle send result."""
        self.send_btn.configure(state="normal")

        if result["success"]:
            self._set_status("✅ Сообщение отправлено!", COLORS["success"])
            history.save_message(recipient, text, "sent")
            self.message_textbox.delete("1.0", "end")
        else:
            self._set_status(f"❌ {result['error']}", COLORS["primary"])
            history.save_message(recipient, text, f"error: {result['error']}")

    def _on_format(self):
        """Handle AI format button click."""
        text = self.message_textbox.get("1.0", "end").strip()
        if not text:
            self._set_status("❌ Нечего форматировать!", COLORS["primary"])
            return

        self._set_status("🤖 AI обрабатывает текст...", COLORS["warning"])
        self.format_btn.configure(state="disabled")

        def _format_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(ai_formatter.format_text(text))
            loop.close()
            self.after(0, lambda: self._on_format_result(result))

        threading.Thread(target=_format_task, daemon=True).start()

    def _on_format_result(self, formatted: str):
        """Handle AI format result."""
        self.format_btn.configure(state="normal")

        if formatted.startswith("["):
            self._set_status(f"❌ {formatted}", COLORS["primary"])
        else:
            self.message_textbox.delete("1.0", "end")
            self.message_textbox.insert("1.0", formatted)
            self._set_status("✨ Текст улучшен AI!", COLORS["success"])

    def _on_history(self):
        """Show history window."""
        HistoryWindow(self)


# ============================================================
# HISTORY WINDOW
# ============================================================
class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("📋 История сообщений")
        self.geometry("650x500")
        self.configure(fg_color=COLORS["bg_dark"])

        # Header
        ctk.CTkLabel(
            self,
            text="📋 История отправленных сообщений",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["success"],
        ).pack(pady=(15, 10))

        # History list
        self.history_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            fg_color=COLORS["bg_card"],
        )
        self.history_textbox.pack(fill="both", expand=True, padx=15, pady=5)

        # Export buttons
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            export_frame,
            text="💾 Экспорт CSV",
            fg_color=COLORS["accent"],
            hover_color="#0a2540",
            corner_radius=8,
            command=self._export_csv,
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkButton(
            export_frame,
            text="💾 Экспорт JSON",
            fg_color=COLORS["accent"],
            hover_color="#0a2540",
            corner_radius=8,
            command=self._export_json,
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

        self._load_history()

    def _load_history(self):
        """Load and display history."""
        messages = history.load_history()
        self.history_textbox.delete("1.0", "end")

        if not messages:
            self.history_textbox.insert("1.0", "История пуста")
            return

        for msg in reversed(messages):
            line = (
                f"[{msg['timestamp'][:16].replace('T', ' ')}] "
                f"→ {msg['recipient']}\n"
                f"   {msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}\n"
                f"   Статус: {msg['status']}\n"
                f"{'─' * 50}\n"
            )
            self.history_textbox.insert("end", line)

    def _export_csv(self):
        """Export history to CSV."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Сохранить как CSV",
        )
        if path:
            history.export_csv(path)
            messagebox.showinfo("Готово", f"История сохранена: {path}")

    def _export_json(self):
        """Export history to JSON."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Сохранить как JSON",
        )
        if path:
            history.export_json(path)
            messagebox.showinfo("Готово", f"История сохранена: {path}")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = TelegramSenderApp()
    app.mainloop()

    # Disconnect Telegram on exit
    asyncio.run(telegram_client.disconnect())
