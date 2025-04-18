# save as poi_bot_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uuid
import json
import os
from datetime import datetime

app = FastAPI()
DATA_PATH = "user_predictions.json"

class PredictionSubmission(BaseModel):
    username: str
    stake: float
    predictions: list[float]
    start_time: str  # ISO timestamp
    strategies: str = ""
    code: str = ""
    link: str = ""

@app.post("/submit")
async def submit_prediction(payload: PredictionSubmission):
    prediction_id = str(uuid.uuid4())
    data = {
        prediction_id: {
            "username": payload.username,
            "stake": payload.stake,
            "submission_time": datetime.utcnow().isoformat(),
            "start_time": payload.start_time,
            "predictions": payload.predictions,
            "strategies": payload.strategies,
            "code": payload.code,
            "link": payload.link
        }
    }

    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            existing = json.load(f)
    else:
        existing = {}

    existing.update(data)

    with open(DATA_PATH, "w") as f:
        json.dump(existing, f, indent=4)

    return {"status": "success", "prediction_id": prediction_id}
