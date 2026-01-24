import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات التصميم (ألوان واضحة واحترافية) ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: 900; font-size: 2.5rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; padding: 20px; border-radius: 12px; border: 2px solid #DEE2E6;
    }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; font-weight: bold !important; }
    .stButton>button { 
        background-color: #0044CC; color: #FFFFFF; border-radius: 10px; font-weight: bold; 
        height: 3.5em; width: 100%; font-size: 1.1rem; border: none;
    }
    .stButton>button:hover { background-color: #003399; color: white; }
    .stSlider > div > div > div > div { background-color: #0044CC; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك جلب أسعار السوق الحقيقية ---
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

# --- 3. إدارة الجلسة (Session State) ---
if 'step' not in st.session_state:
    live_prices = get_live_prices()
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': live_prices,
        'event': "📢 System Ready: Configure your portfolio to start."
    })

# --- 4. معالجة الجولات والأحداث الاقتصادية ---
def process_turn():
    scenarios = [
        {"msg": "🚀 TECH BOOM: AI innovations drive Equity prices higher!", "e": 0.12, "f": -0.02, "c": -0.04},
        {"msg": "⚠️ MARKET VOLATILITY: Investors flee to Gold for safety.", "e": -0.08, "f": 0.05, "c": 0.15},
        {"msg": "🏦 RATE HIKE: Central bank increases interest rates.", "e": -0.05, "f": -0.10, "c": -0.02}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    # حساب القيمة الإجمالية (كاش + استثمارات)
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 5. واجهة المستخدم (UI) ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | News: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH BALANCE", f"${st.session_state.balance:,.0f}")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI %", f"{roi:.2f}%")

    with st.form("investment_form"):
        st.write("### Adjust Asset Allocation")
        s_pct = st.slider("Stocks (Equities) %", 0, 100, 40)
        b_pct = st.slider("Bonds (Fixed Income) %", 0, 100, 30)
        g_pct = st.slider("Gold (Commodities) %", 0, 100, 30)
        
        if st.form_submit_button("EXECUTE STRATEGY"):
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

# --- 6. صفحة النتائج النهائية ونظام الإرسال (Web3Forms API) ---
else:
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    st.success("🎯 Simulation Completed! Your final report is ready.")
    
    # رسم بياني للأداء
    fig
