"""
Telegram Salon Messenger — Web GUI (Flask)
by keml00, Telegram

Web interface for sending Telegram messages without saving contacts.
Run: python app.py -> open http://localhost:5000
"""

import threading
from flask import Flask, render_template, request, jsonify, send_file
import telegram_client
import ai_formatter
import history
import tempfile

app = Flask(__name__)


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send():
    """Send message endpoint."""
    data = request.json
    recipient = data.get("recipient", "").strip()
    text = data.get("text", "").strip()

    if not recipient:
        return jsonify({"success": False, "error": "Укажите получателя"})
    if not text:
        return jsonify({"success": False, "error": "Введите сообщение"})

    result = telegram_client.send_message(recipient, text)

    if result["success"]:
        history.save_message(recipient, text, "sent")
    else:
        history.save_message(recipient, text, f"error: {result['error']}")

    return jsonify(result)


@app.route("/format", methods=["POST"])
def format_text_route():
    """AI format text endpoint."""
    data = request.json
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"success": False, "error": "Нечего форматировать"})

    result = ai_formatter.format_text(text)

    if result.startswith("["):
        return jsonify({"success": False, "error": result})

    return jsonify({"success": True, "text": result})


@app.route("/history")
def get_history():
    """Get message history."""
    messages = history.load_history()
    return jsonify(messages)


@app.route("/export/<fmt>")
def export(fmt):
    """Export history as CSV or JSON."""
    if fmt == "csv":
        path = tempfile.mktemp(suffix=".csv")
        history.export_csv(path)
        return send_file(path, as_attachment=True, download_name="history.csv")
    elif fmt == "json":
        path = tempfile.mktemp(suffix=".json")
        history.export_json(path)
        return send_file(path, as_attachment=True, download_name="history.json")

    return jsonify({"error": "Invalid format"}), 400


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    import webbrowser

    print("\n" + "=" * 50)
    print("  Telegram Salon Messenger")
    print("=" * 50)

    # Auth Telegram BEFORE starting Flask (uses telethon.sync)
    if telegram_client.API_ID and telegram_client.API_HASH:
        print("\n  Connecting to Telegram...")
        print("  If code is needed — enter it below:\n")
        try:
            telegram_client.init_client()
            print("\n  Telegram connected!\n")
        except Exception as e:
            print(f"\n  Connection error: {e}")
            print("  App will start but sending won't work.\n")
    else:
        print("\n  TELEGRAM_API_ID / API_HASH not set in .env")
        print("  Fill them and restart.\n")

    print("  Opening: http://localhost:5000\n")

    # Auto-open browser
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()

    app.run(host="127.0.0.1", port=5000, debug=False)
