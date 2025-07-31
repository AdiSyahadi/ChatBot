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
    data = request.json

    try:
        msg = {
            "from": data['messages'][0]['from'].split('@')[0],
            "text": data['messages'][0]['text']['body'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "replied": False
        }

        # Load file JSON lama
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                messages = json.load(f)
        else:
            messages = []

        messages.append(msg)

        # Simpan kembali
        with open(DATA_FILE, "w") as f:
            json.dump(messages, f, indent=2)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
