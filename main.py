import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. التصميم الرسمي الأبيض ---
st.set_page_config(page_title="Professional Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; border: 1px solid #D1D5DB; border-radius: 10px; padding: 20px; 
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.2rem !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; font-weight: bold !important; }
    .result-certificate { 
        background-color: #F0F9FF; border: 2px solid #0044CC; border-radius: 15px; 
        padding: 40px; text-align: center; margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 2. إدارة البيانات ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'event': "📢 System Ready. Configure your first allocation."
    })

with st.sidebar:
    st.header("⚙️ Control Panel")
    if st.button("🔄 Restart Simulation"):
        reset_game()

def process_turn():
    scenarios = [
        {"msg": "🚀 Market Growth: Tech sector rally!", "e": 0.08, "f": -0.01, "c": -0.02},
        {"msg": "⚠️ Volatility Alert: Gold is rising.", "e": -0.05, "f": 0.02, "c": 0.10}
    ]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 3. الواجهة ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    st.info(f"Round: {st.session_state.step} of 5 | {st.session_state.event}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("Current ROI", f"{roi:.2f}%")

    with st.form("trades"):
        st.write("### Portfolio Allocation")
        col_a, col_b, col_c = st.columns(3)
        s = col_a.slider("Equities %", 0, 100, 40)
        b = col_b.slider("Fixed Income %", 0, 100, 30)
        g = col_c.slider("Commodities %", 0, 100, 30)
        if st.form_submit_button("EXECUTE TRADES"):
            if s + b + g > 100:
                st.error("Error: Total exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.
