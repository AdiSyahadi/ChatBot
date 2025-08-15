# chatbot/webhook_receiver.py

from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)
DATA_FILE = "data_customer/messages.json"

# Pastikan folder data_customer sudah ada
os.makedirs("data_customer", exist_ok=True)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Coba ambil data mentah
        raw_data = request.data.decode("utf-8", errors="ignore")
        
        # Coba parse ke JSON kalau memungkinkan
        try:
            data = json.loads(raw_data)
            parsed_ok = True
        except json.JSONDecodeError:
            data = raw_data  # simpan sebagai teks mentah
            parsed_ok = False

        # Bangun pesan
        if parsed_ok and "messages" in data:
            msg = {
                "from": data['messages'][0]['from'].split('@')[0],
                "text": data['messages'][0]['text']['body'],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "replied": False
            }
        else:
            # Kalau bukan format JSON WA, simpan sebagai raw string
            msg = {
                "from": "unknown",
                "text": raw_data.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "replied": False
            }

        # Load file JSON lama
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            messages = []

        messages.append(msg)

        # Simpan kembali
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({
            "error": str(e),
            "raw_data": request.data.decode("utf-8", errors="ignore")
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
