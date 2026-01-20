import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests
from io import BytesIO

# --- Configuration ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

# --- Custom Styling (Gold & Dark Professional) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-weight: 800; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
    }
    .stButton>button { 
        background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%);
        color: black; font-weight: bold; border-radius: 8px; border: none; height: 3em;
    }
    .stTextInput>div>div>input { background-color: #161b22; color: white; border: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Georgia', serif; }
    </style>
    """, unsafe_allow_html=True)

# --- Fetch Real Market Data ---
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
        return {"Equities": 450.0, "Fixed Income": 95.0, "Commodities": 180.0}

# --- Session State ---
if 'step' not in st.session_state:
    live_prices = get_live_prices()
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': live_prices,
        'initial_prices': live_prices.copy(),
        'event': "Market Terminal Online. Deploy your capital."
    })

# --- Market Engine ---
def simulate_market_move():
    volatility = {"Equities": 0.06, "Fixed Income": 0.02, "Commodities": 0.04}
    for asset in st.session_state.prices:
        change = np.random.normal(0.001, volatility[asset])
        st.session_state.prices[asset] *= (1 + change)
    
    val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(val)
    st.session_state.step += 1

# --- Interface ---
st.title("🏛️ Professional Investment Strategy Lab")
st.caption("Graduate Level Simulation | Live Market Benchmarks")

if st.session_state.step <= 5:
    # Dashboard
    st.info(f"📅 **Trading Round:** {st.session_state.step} of 5 | 📢 **Last Move:** {st.session_state.event}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("CASH LIQUIDITY", f"${st.session_state.balance:,.0f}")
    m2.metric("CURRENT AUM", f"${st.session_state.history[-1]:,.0f}")
    roi_current = ((st.session_state.history[-1] - 1000000)/1000000)*100
    m3.metric("CURRENT ROI", f"{roi_current:.2f}%")

    with st.form("trade_form"):
        st.write("### 🛠️ Strategic Asset Allocation")
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Equities (SPY) %", 0, 100, 0)
        b_pct = c2.slider("Fixed Income (TLT) %", 0, 100, 0)
        g_pct = c3.slider("Commodities (GLD) %", 0, 100, 0)
        
        if st.form_submit_button("EXECUTE PORTFOLIO REBALANCING"):
            if s_pct + b_pct + g_pct > 100:
                st.error("Compliance Error: Total allocation cannot exceed 100%.")
            else:
                total_w = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (total_w * (s_pct/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (total_w * (b_pct/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (total_w * (g_pct/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = total_w * (1 - (s_pct+b_pct+g_pct)/100)
                simulate_market_move()
                st.rerun()

# --- Results & Optional Submission ---
else:
    st.success("🎯 Simulation Concluded. Review your final performance.")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#d4af37', width=4), fill='tozeroy'))
    fig.update_layout(template="plotly_dark", title="Equity Growth Curve", xaxis_title="Round", yaxis_title="Net Worth ($)")
    st.plotly_chart(fig, use_container_width=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write("### 📊 Performance Summary")
        st.metric("FINAL AUM", f"${final_aum:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart to Improve Score"):
            st.session_state.clear()
            st.rerun()

    with col_res2:
        st.write("### 📧 Submit to Instructor")
        st.write("If you are satisfied with your results, enter your details below.")
        s_name = st.text_input("Your Full Name:")
        i_email = st.text_input("Instructor Email:")
        
        if st.button("Submit Audited Report"):
            if s_name and i_email and "@" in i_email:
                data = {
                    "Student": s_name,
                    "Final_AUM": f"${final_aum:,.2f}",
                    "ROI": f"{total_roi:.2f}%",
                    "Status": "Graduate Level Simulation Completed"
                }
                requests.post(f"https://formsubmit.co/ajax/{i_email}", data=data)
                st.balloons()
                st.success(f"Report for {s_name} has been sent successfully!")
            else:
                st.error("Please provide both name and valid email.")
