import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات الواجهة ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: bold; }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; }
    .stButton>button { background-color: #0044CC; color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب البيانات ---
@st.cache_data(ttl=3600)
def get_live_prices():
    try:
        tickers = {"Equities": "SPY", "Fixed Income": "TLT", "Commodities": "GLD"}
        prices = {}
        for label, ticker in tickers.items():
            data = yf.Ticker(ticker).history(period="1d")
            prices[label] = round(data['Close'].iloc[-1], 2)
        return prices
    except:
        return {"Equities": 480.0, "Fixed Income": 95.0, "Commodities": 185.0}

# --- 3. إدارة الحالة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "📢 System Ready."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Tech Rally!", "e": 0.10, "f": -0.02, "c": -0.03},
        {"msg": "⚠️ Market Volatility", "e": -0.07, "f": 0.03, "c": 0.12},
        {"msg": "🏦 Rate Hike", "e": -0.05, "f": -0.08, "c": -0.02}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. العرض ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"Round {st.session_state.step} of 5 | {st.session_state.event}")
    st.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    
    with st.form("trade"):
        s = st.slider("Equities %", 0, 100, 40)
        b = st.slider("Bonds %", 0, 100, 30)
        g = st.slider("Gold %", 0, 100, 30)
        if st.form_submit_button("Submit Step"):
            if s + b + g > 100:
                st.error("Exceeds 100%!")
            else:
                val = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (val * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (val * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (val * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = val * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- الجزء الذي كان فيه الخطأ تم إصلاحه هنا ---
else:
    st.success("🎯 Simulation Completed!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # تعريف الرسم البياني بشكل صحيح
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC')))
    fig.update_layout(title="Performance Chart", plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Final ROI", f"{total_roi:.2f}%")
        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()

    with c2:
        st.write("### Email Submission")
        s_name = st.text_input("Name:")
        i_email = st.text_input("Instructor Email:")
        if st.button("Send Report"):
            # استخدام Web3Forms
            res = requests.post("https://api.web3forms.com/submit", data={
                "access_key": "7649525c-4820-474c-a19c-85a085d38865",
                "subject": f"Result: {s_name}",
                "to_email": i_email,
                "Student": s_name,
                "ROI": f"{total_roi:.2f}%"
            })
            if res.status_code == 200:
                st.balloons()
                st.success("Sent Successfully!")
                
