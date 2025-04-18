import streamlit as st
import pandas as pd
import numpy as np
import ccxt
import time
import datetime
import uuid
import os
import json

# --- Config ---
DATA_PATH = "user_predictions.json"

# --- Streamlit Setup ---
st.set_page_config(page_title="Proof of Insight", layout="wide")
st.title("🔮 Proof of Insight - BTC/USDT Forecast")

# --- Initialize Session State ---
for key in ['user_data_store', 'prediction_results', 'feedback_flags']:
    if key not in st.session_state:
        st.session_state[key] = {}

# --- Load bot/user shared predictions ---
def load_bot_predictions():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            bot_data = json.load(f)
        for pred_id, entry in bot_data.items():
            if pred_id not in st.session_state.user_data_store:
                st.session_state.user_data_store[pred_id] = entry

# --- Fetch price data ---
def fetch_ohlcv(symbol="BTC/USDT", timeframe='1m', limit=200):
    try:
        exchange = ccxt.kucoin()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        return df
    except Exception as e:
        st.error(f"Failed to fetch data from KuCoin: {e}")
        return pd.DataFrame()

# --- Calculate next round start time ---
def get_next_round_start():
    now = datetime.datetime.utcnow()
    minute = ((now.minute // 5) + 1) * 5
    next_time = now.replace(second=0, microsecond=0)
    if minute >= 60:
        next_time += datetime.timedelta(hours=1)
        next_time = next_time.replace(minute=0)
    else:
        next_time = next_time.replace(minute=minute)
    return next_time

# --- Scoring Function ---
def calculate_score(predictions, actuals):
    errors = np.abs((np.array(predictions) - np.array(actuals)) / np.array(actuals)) * 100
    weights = np.exp(np.linspace(0, -2, len(errors)))
    weights /= weights.sum()
    weighted_error = np.sum(errors * weights)
    score = 100 - (weighted_error * 1.5)
    return max(0, min(100, score)), weighted_error, errors

# --- Reward Function ---
def calculate_reward(score, stake):
    tiers = {
        'Bronze': (85, 1.0),
        'Silver': (90, 1.5),
        'Gold': (95, 2.5),
        'Platinum': (98, 4.0)
    }
    for _, (threshold, multiplier) in reversed(tiers.items()):
        if score >= threshold:
            return round(stake * multiplier, 2)
    return 0.0

# --- Login Section ---
st.subheader("👤 User Login")
username = st.text_input("Enter your username:")
stake = st.number_input("Stake USDC (e.g., 10)", min_value=1.0, value=10.0)

if username:
    load_bot_predictions()
    next_round = get_next_round_start()
    st.markdown(f"⏱️ **Next round starts at:** `{next_round.strftime('%Y-%m-%d %H:%M:%S')} UTC`")

    # --- Prediction Input ---
    st.subheader("📈 Submit Predictions (Next 7 candles)")
    cols = st.columns(7)
    predictions = [cols[i].number_input(f"Prediction {i + 1}", key=f"pred_{i}") for i in range(7)]

    prediction_id = str(uuid.uuid4())
    if st.button("Submit Predictions"):
        submission_time = datetime.datetime.utcnow()
        st.session_state.user_data_store[prediction_id] = {
            'username': username,
            'stake': stake,
            'submission_time': submission_time,
            'start_time': next_round,
            'predictions': predictions,
            'strategies': '',
            'code': '',
            'link': ''
        }
        st.session_state.feedback_flags[prediction_id] = [False] * 7

        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r") as f:
                    all_data = json.load(f)
            else:
                all_data = {}
            all_data[prediction_id] = st.session_state.user_data_store[prediction_id]
            with open(DATA_PATH, "w") as f:
                json.dump(all_data, f, default=str)
            st.success(f"✅ Predictions submitted at {submission_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        except Exception as e:
            st.error(f"❌ Error saving prediction: {e}")

    # --- Strategy Submission ---
    st.subheader("🧠 Strategy")
    strategy_text = st.text_area("Describe your method:")
    code_text = st.text_area("Optional Code Snippet:")
    link = st.text_input("Or link to GitHub/Colab:")

    if st.button("Submit Strategy"):
        recent_pred_id = None
        for pid in reversed(list(st.session_state.user_data_store.keys())):
            if st.session_state.user_data_store[pid]['username'] == username:
                recent_pred_id = pid
                break
        if recent_pred_id:
            st.session_state.user_data_store[recent_pred_id]['strategies'] = strategy_text
            st.session_state.user_data_store[recent_pred_id]['code'] = code_text
            st.session_state.user_data_store[recent_pred_id]['link'] = link
            st.success("✅ Strategy attached.")
        else:
            st.warning("⚠️ No recent prediction found.")

# --- Feedback Section ---
st.subheader("📊 Prediction Feedback")
df = fetch_ohlcv().set_index('datetime')

for pred_id, record in st.session_state.user_data_store.items():
    username_ = record.get("username", "Unknown")
    start_time = pd.Timestamp(record['start_time'], tz='UTC')
    actuals = df[df.index >= start_time]['close'].head(7)

    st.markdown(f"### Feedback for `{username_}`")
    st.markdown(f"📅 Start Time: `{start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC`")
    st.markdown(f"🕒 Submitted: `{record['submission_time']}`")

    if pred_id not in st.session_state.feedback_flags:
        st.session_state.feedback_flags[pred_id] = [False] * 7

    for i in range(7):
        candle_time = start_time + pd.Timedelta(minutes=i)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"Candle {i+1} — `{candle_time.strftime('%H:%M:%S')} UTC`")
        with col2:
            if st.button(f"Feedback {i+1}", key=f"fb_{pred_id}_{i}"):
                st.session_state.feedback_flags[pred_id][i] = True

        if st.session_state.feedback_flags[pred_id][i]:
            if candle_time in actuals.index:
                actual_price = actuals.loc[candle_time]
                pred = record['predictions'][i]
                err = abs((pred - actual_price) / actual_price) * 100
                st.markdown(f"- 🎯 Prediction: `{pred}`")
                st.markdown(f"- 📈 Actual: `{actual_price}`")
                st.markdown(f"- ❗ Error: `{err:.2f}%`")
            else:
                st.info(f"Candle {i+1} at `{candle_time.strftime('%H:%M:%S')}` not closed yet.")

    # Final summary if all 7 actuals are available
    if len(actuals) == 7 and pred_id not in st.session_state.prediction_results:
        score, avg_err, errors = calculate_score(record['predictions'], actuals.tolist())
        reward = calculate_reward(score, record['stake'])

        st.session_state.prediction_results[pred_id] = {
            'actuals': actuals.tolist(),
            'errors': errors.tolist(),
            'avg_err': avg_err,
            'score': score,
            'reward': reward
        }

    if pred_id in st.session_state.prediction_results:
        res = st.session_state.prediction_results[pred_id]
        st.markdown("#### ✅ Final Summary")
        st.markdown(f"**Average Error:** `{res['avg_err']:.2f}%`")
        st.markdown(f"**Insight Score:** `{res['score']:.2f}`")
        st.markdown(f"**Reward:** `{res['reward']} USDC`")

# --- Rerun Button ---
if username:
    if st.button("🔁 Predict Again"):
        st.experimental_rerun()

