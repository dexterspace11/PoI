# 📈 PoI Prediction App (FastAPI + Flask Bot Integration)

This project allows bots to submit future price predictions and stake values through a Flask interface. These predictions are received and managed by a FastAPI server and stored in a local `user_predictions.json` file.

---

## 📦 Structure


---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
python poi_bot_api.py
python -m uvicorn PoI_app:FastAPI --reload
python bot_submit.py
import requests

url = "http://127.0.0.1:5000/submit"
payload = {
    "username": "MyBot",
    "stake": 10,
    "predictions": [30100, 30200, 30300, 30400, 30500, 30600, 30700],
    "strategies": "Simple moving average strategy",
    "code": "https://github.com/yourname/mybot",
    "link": ""
}
response = requests.post(url, json=payload)
print(response.text)
