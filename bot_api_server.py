from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

# Store predictions in a shared JSON file
DATA_FILE = "external_predictions.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)

@app.route("/submit", methods=["POST"])
def submit_prediction():
    data = request.json

    # Validate input
    required_keys = {"username", "stake", "predictions", "start_time"}
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields"}), 400

    if len(data["predictions"]) != 7:
        return jsonify({"error": "You must submit exactly 7 predictions."}), 400

    pred_id = str(uuid.uuid4())
    submission = {
        "username": data["username"],
        "stake": float(data["stake"]),
        "submission_time": datetime.utcnow().isoformat(),
        "start_time": data["start_time"],  # must be UTC timestamp string
        "predictions": data["predictions"],
        "strategies": data.get("strategies", ""),
        "code": data.get("code", ""),
        "link": data.get("link", "")
    }

    predictions = load_data()
    predictions[pred_id] = submission
    save_data(predictions)

    return jsonify({"message": "Prediction submitted successfully", "prediction_id": pred_id})

if __name__ == "__main__":
    app.run(port=5001)
