import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="Strategic Investment Simulator", layout="wide")

# PROFESSIONAL CORPORATE DESIGN (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stMetricValue"] { font-size: 2.2rem; color: #1E3A8A; font-weight: 700; }
    div[data-testid="stMetric"] { 
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        border: 1px solid #e2e8f0; 
    }
    .stSlider > div > div > div > div { background-color: #1E3A8A; }
    .stButton>button { 
        background-color: #1E3A8A; 
        color: white; 
        border-radius: 12px; 
        border: none; 
        font-size: 1.1rem; 
        font-weight: bold;
        height: 3.5em;
        transition: 0.3s; 
    }
    .stButton>button:hover { background-color: #2563EB; transform: translateY(-2px); }
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.balance = 1000000.0
    st.session_state.portfolio = {"Stocks": 0, "Bonds": 0, "Gold": 0}
    st.session_state.history = [1000000.0]
    st.session_state.prices = {"Stocks": 200.0, "Bonds": 100.0, "Gold": 1800.0}
    st.session_state.event = "System Ready: Define your initial capital allocation."

def next_turn():
    events = [
        {"msg": "Global tech rally boosts equity markets!", "stocks": 0.15, "bonds": 0.01, "gold": -0.05},
        {"msg": "Central Bank interest rate hike announced.", "stocks": -0.10, "bonds": -0.05, "gold": -0.02},
        {"msg": "Geopolitical uncertainty increases demand for Gold.", "stocks": -0.12, "bonds": 0.04, "gold": 0.10},
        {"msg": "Inflation data is lower than expected; market stabilizes.", "stocks": 0.08, "bonds": 0.06, "gold": -0.04}
    ]
    selected_event = np.random.choice(events)
    st.session_state.event = selected_event["msg"]
    st.session_state.prices["Stocks"] *= (1 + selected_event["stocks"])
    st.session_state.prices["Bonds"] *= (1 + selected_event["bonds"])
    st.session_state.prices["Gold"] *= (1 + selected_event["gold"])
    
    current_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(current_val)
    st.session_state.step += 1

# Interface
st.title("📊 Strategic Investment Simulator")
st.markdown("### Decision Support System for MIS Master's Students")
st.divider()

st.info(f"📅 **Round:** {st.session_state.step} of 5 | 📢 **Market Update:** {st.session_state.event}")

m1, m2, m3 = st.columns(3)
m1.metric("Available Cash", f"${st.session_state.balance:,.2f}")
m2.metric("Portfolio Net Worth", f"${st.session_state.history[-1]:,.2f}")
m3.metric("Simulation Progress", f"{int((st.session_state.step/5)*100)}%")

if st.session_state.step <= 5:
    st.write("#### ⚙️ Asset Allocation Strategy")
    with st.form("trade_form"):
        col_s, col_b, col_g = st.columns(3)
        s_pct = col_s.slider("Stocks (%)", 0, 100, 0)
        b_pct = col_b.slider("Bonds (%)", 0, 100, 0)
        g_pct = col_g.slider("Gold (%)", 0, 100, 0)
        
        if st.form_submit_button("Confirm Allocation & Proceed"):
            if s_pct + b_pct + g_pct > 100:
                st.error("Error: Total allocation cannot exceed 100%!")
            else:
                total_w = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
                st.session_state.portfolio["Stocks"] = (total_w * (s_pct/100)) / st.session_state.prices["Stocks"]
                st.session_state.portfolio["Bonds"] = (total_w * (b_pct/100)) / st.session_state.prices["Bonds"]
                st.session_state.portfolio["Gold"] = (total_w * (g_pct/100)) / st.session_state.prices["Gold"]
                st.session_state.balance = total_w * (1 - (s_pct+b_pct+g_pct)/100)
                next_turn()
                st.rerun()
else:
    st.success("🎯 Simulation Completed Successfully.")
    final_v = st.session_state.history[-1]
    roi = ((final_v - 1000000)/1000000)*100
    
    # Results visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#1E3A8A', width=4)))
    fig.update_layout(title="Performance Growth Curve", xaxis_title="Round", yaxis_title="Value ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Excel Report
    report_df = pd.DataFrame({"Metric": ["Final Worth", "ROI %"], "Value": [f"${final_v:,.2f}", f"{roi:.2f}%"]})
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        report_df.to_excel(wr, index=False)
    st.download_button("📥 Download Instructor's Assessment Report", data=buf.getvalue(), file_name="student_report.xlsx")
    if st.button("Restart Session"):
        st.session_state.clear()
        st.rerun()
