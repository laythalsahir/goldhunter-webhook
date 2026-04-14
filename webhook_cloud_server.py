from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)

latest_signal = {
    "action": "WAIT",
    "sl": 0.0,
    "tp": 0.0,
    "timestamp": 0.0,
    "consumed": True
}

SECRET_KEY = os.environ.get("SECRET_KEY", "goldhunter2024")


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "GoldHunter Webhook Server is RUNNING",
        "last_signal": latest_signal["action"],
        "time": latest_signal["timestamp"]
    })


@app.route('/tv_webhook', methods=['POST'])
def receive_webhook():
    global latest_signal
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data"}), 400
        if data.get("key") != SECRET_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        action = str(data.get("action", "WAIT")).upper()
        if action not in ["BUY", "SELL", "CLOSE"]:
            return jsonify({"error": f"Unknown action: {action}"}), 400
        sl = float(data.get("sl", 0.0))
        tp = float(data.get("tp", 0.0))
        if action in ["BUY", "SELL"] and (sl == 0.0 or tp == 0.0):
            return jsonify({"error": "SL/TP cannot be zero"}), 400
        latest_signal = {
            "action": action,
            "sl": sl,
            "tp": tp,
            "timestamp": time.time(),
            "consumed": False
        }
        print(f"Signal: {action} | SL={sl} | TP={tp}")
        return jsonify({"status": "ok", "signal": action}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_signal', methods=['GET'])
def get_signal():
    global latest_signal
    if not latest_signal["consumed"]:
        latest_signal["consumed"] = True
        return jsonify({
            "new": True,
            "action": latest_signal["action"],
            "sl": latest_signal["sl"],
            "tp": latest_signal["tp"],
            "timestamp": latest_signal["timestamp"]
        })
    else:
        return jsonify({"new": False, "action": "WAIT"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
