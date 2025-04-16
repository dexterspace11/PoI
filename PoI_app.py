# app.py
import streamlit as st
import pandas as pd
import datetime
import os

# Create a folder to store data
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/predictions.csv"

st.set_page_config(page_title="Proof of Insight", layout="wide")
st.title("🔮 Proof of Insight")
st.subheader("Predict the future, earn from insight.")

# --- FORM ---
with st.form("prediction_form"):
    st.markdown("### Submit Your Prediction")

    username = st.text_input("Username (or alias)", max_chars=20)
    pair = st.selectbox("Crypto Pair", ["BTC/USDT"])
    timeframe = st.selectbox("Time Frame", ["1H", "4H", "1D"])
    start_date = st.date_input("Prediction Start Date", datetime.date.today())
    stake = st.number_input("Simulated Stake (USDC)", min_value=5.0, value=5.0, step=1.0)

    st.markdown("#### Predicted OHLC for 14 Periods")
    predictions = []
    for i in range(1, 15):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            open_price = st.number_input(f"Period {i} - Open", key=f"open_{i}")
        with col2:
            high_price = st.number_input(f"High", key=f"high_{i}")
        with col3:
            low_price = st.number_input(f"Low", key=f"low_{i}")
        with col4:
            close_price = st.number_input(f"Close", key=f"close_{i}")
        predictions.append({
            "period": i,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price
        })

    analysis = st.text_area("Your Analysis", height=150, help="Explain why you made your prediction.")

    submit = st.form_submit_button("Submit Prediction")

    if submit:
        timestamp = datetime.datetime.now().isoformat()
        rows = []
        for p in predictions:
            rows.append({
                "timestamp": timestamp,
                "username": username,
                "pair": pair,
                "timeframe": timeframe,
                "start_date": start_date,
                "stake": stake,
                "period": p["period"],
                "open": p["open"],
                "high": p["high"],
                "low": p["low"],
                "close": p["close"],
                "analysis": analysis
            })
        df = pd.DataFrame(rows)

        # Save to CSV
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, mode='a', index=False, header=False)
        else:
            df.to_csv(DATA_FILE, index=False)

        st.success("✅ Prediction submitted successfully!")

