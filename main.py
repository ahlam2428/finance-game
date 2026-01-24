import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات الواجهة (التصميم الملكي الذي اتفقنا عليه) ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 15px; }
    h1, h2, h3, p, label { color: white !important; font-family: 'Arial'; }
    .stButton>button { 
        background-color: #0044CC; color: white; border-radius: 8px; font-weight: bold; 
        height: 3em; width: 100%; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00D1FF; color: black; }
    .stSlider > div > div > div > div { background-color: #00D1FF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك جلب الأسعار الحية ---
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
        return {"Equities": 485.0, "Fixed Income": 94.5, "Commodities": 182.0}

# --- 3. تهيئة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "📢 System Ready: Configure your first allocation."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Tech Rally!", "e": 0.10, "f": -0.02, "c": -0.03},
        {"msg": "⚠️ Market Volatility", "e": -0.08, "f": 0.04, "c": 0.12},
        {"msg": "🏦 Rate Hike", "e": -0.05, "f": -0.10, "c": -0.02},
        {"msg": "📈 Growth Spike", "e": 0.07, "f": 0.02, "c": 0.05}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. واجهة المستخدم ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | News: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH", f"${st.session_state.balance:,.0f}")
    col2.metric("TOTAL VALUE", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("ROI %", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.write("### Adjust Allocation")
        s = st.slider("Equities %", 0, 100, 40)
        b = st.slider("Bonds %", 0, 100, 30)
        g = st.slider("Gold %", 0, 100, 30)
        
        if st.form_submit_button("EXECUTE ALLOCATION"):
            if s + b + g > 100:
                st.error("Total exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. صفحة النتائج النهائية ---
else:
    st.success("🎯 Simulation Completed!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # إصلاح الرسم البياني
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#00D1FF', width=3)))
    fig.update_layout(title="Equity Growth Curve", template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("FINAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart"):
            st.session_state.clear()
            st.rerun()

    with c2:
        st.write("### 📧 Send Report")
        s_name = st.text_input("Name:")
        i_email = st.text_input("Instructor Email:")
        if st.button("Send Audited Results"):
            if s_name and i_email:
                # إرسال عبر Web3Forms
                res = requests.post("https://api.web3forms.com/submit", data={
                    "access_key": "7649525c-4820-474c-a19c-85a085d38865",
                    "subject": f"Lab Result: {s_name}",
                    "to_email": i_email,
                    "Student": s_name,
                    "Final ROI": f"{total_roi:.2f}%",
                    "Final Value": f"${final_aum:,.2f}"
                })
                if res.status_code == 200:
                    st.balloons()
                    st.success(f"Sent to {i_email}!")
                else:
                    st.error("Submission failed.")
            else:
                st.warning("Please fill name and email.")
