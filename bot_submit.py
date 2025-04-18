# bot_submit.py

import json
import uuid
import datetime
import os

DATA_PATH = "user_predictions.json"  # Make sure this matches your FastAPI path

def submit_bot_prediction(username="BotAlpha", stake=10, predictions=None):
    if predictions is None:
        predictions = [30000 + i * 10 for i in range(7)]  # Replace with your logic

    prediction_id = str(uuid.uuid4())
    start_time = datetime.datetime.utcnow().replace(second=0, microsecond=0)

    bot_entry = {
        "username": username,
        "stake": stake,
        "submission_time": datetime.datetime.utcnow().isoformat(),
        "start_time": start_time.isoformat(),
        "predictions": predictions,
        "strategies": "Bot strategy: Random forecast",
        "code": "",
        "link": ""
    }

    # Load existing predictions
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            all_data = json.load(f)
    else:
        all_data = {}

    all_data[prediction_id] = bot_entry

    # Save updated data
    with open(DATA_PATH, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"✅ Bot prediction submitted with ID: {prediction_id}")

if __name__ == "__main__":
    submit_bot_prediction()
