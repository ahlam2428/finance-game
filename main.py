import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات التصميم الاحترافي الواضح ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: 900; font-size: 2.8rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; padding: 20px; border-radius: 12px; border: 2px solid #DEE2E6;
    }
    h1, h2, h3, h4, p, label { color: #000000 !important; font-weight: bold !important; font-family: 'Arial'; }
    .stButton>button { 
        background-color: #0044CC; color: #FFFFFF; border-radius: 8px; font-weight: 900; 
        height: 3.5em; width: 100%; font-size: 1.2rem; border: none;
    }
    .stButton>button:hover { background-color: #003399; color: #FFFFFF; }
    .stSlider > div > div > div > div { background-color: #0044CC; }
    .stAlert { background-color: #E7F0FF; color: #000000; border: 1px solid #0044CC; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب بيانات السوق الحية ---
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

# --- 3. تهيئة الجلسة ---
if 'step' not in st.session_state:
    live_prices = get_live_prices()
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': live_prices,
        'event': "📢 System Ready. Hover over terms to learn more."
    })

# --- 4. محرك الأخبار والنتائج ---
def process_turn():
    scenarios = [
        {"msg": "🚀 TECH BOOM: AI innovations drive stock prices higher!", "e": 0.10, "f": -0.01, "c": -0.03},
        {"msg": "⚠️ GEOPOLITICAL RISK: Uncertainty pushes investors toward Gold.", "e": -0.07, "f": 0.03, "c": 0.12},
        {"msg": "🏦 RATE HIKE: Central bank increases rates; Bonds and Stocks drop.", "e": -0.05, "f": -0.08, "c": -0.02},
        {"msg": "📉 GLOBAL SLOWDOWN: Consumer demand weakens across sectors.", "e": -0.12, "f": 0.05, "c": 0.04},
        {"msg": "🔥 ENERGY SURGE: Commodities spike amid supply constraints.", "e": -0.03, "f": -0.02, "c": 0.15}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 5. واجهة اللعب ---
st.title("🏛️ Investment Strategy & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH", f"${st.session_state.balance:,.0f}", help="Available funds to invest.")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}", help="Total value of cash + investments.")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("ROI %", f"{roi:.2f}%", help="Return on Investment relative to $1M starting capital.")

    with st.form("trade_form"):
        st.write("### 🛠️ Portfolio Rebalancing")
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Stocks (SPY) %", 0, 100, 0, help="High risk/reward equity index.")
        b_pct = c2.slider("Bonds (TLT) %", 0, 100, 0, help="Long-term government treasury bonds.")
        g_pct = c3.slider("Gold (GLD) %", 0, 100, 0, help="Safe haven asset for crises.")
        
        if st.form_submit_button("EXECUTE ALLOCATION", help="Confirm your strategy for this round."):
            if s_pct + b_pct + g_pct > 100:
                st.error("Error: Total allocation exceeds 100%!")
            else:
                total_w = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (total_w * (s_pct/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (total_w * (b_pct/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (total_w * (g_pct/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = total_w * (1 - (s_pct+b_pct+g_pct)/100)
                process_turn()
                st.rerun()

# --- 6. النتائج النهائية ونظام الإرسال المرن ---
else:
    st.success("🎯 Simulation Completed. Review your results.")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history))), y=st.session_state.history, 
        mode='lines+markers', line=dict(color='#0044CC', width=5), marker=dict(size=10)
    ))
    fig.update_layout(title="Growth Path", xaxis=dict(title="Round", dtick=1), yaxis=dict(title="Value ($)"), plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    res1, res2 = st.columns(2)
    with res1:
        st.metric("FINAL NET WORTH", f"${final_aum:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart Simulation"):
            st.session_state.clear()
            st.rerun()

    with res2:
        st.write("### 📧 Send Report to Instructor")
        name = st.text_input("Student Name:")
        email = st.text_input("Instructor Email:")
        if st.button("Send Audited Results"):
            if name and email and "@" in email:
                payload = {
                    "Student": name, "ROI": f"{total_roi:.2f}%", 
                    "Final_Value": f"${final_aum:,.2f}", "_subject": f"Lab Result: {name}"
                }
                # الإرسال المباشر لضمان التوافق
                requests.post(f"https://formsubmit.co/{email}", data=payload)
                st.balloons()
                st.success(f"Sent! Instructor must check email to 'Activate' first submission.")
            else:
                st.warning("Please enter a valid name and email.")
                
