import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="Investment Portfolio Simulator", layout="wide")

# PROFESSIONAL CORPORATE DESIGN (Finance Blue Theme)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { font-size: 2.2rem; color: #002D62; font-weight: 700; }
    div[data-testid="stMetric"] { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
        border-top: 5px solid #002D62; 
    }
    .stSlider > div > div > div > div { background-color: #002D62; }
    .stButton>button { 
        background-color: #002D62; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        font-size: 1.1rem; 
        font-weight: bold;
        height: 3.5em;
        width: 100%;
    }
    .stButton>button:hover { background-color: #004080; border: 1px solid #002D62; }
    h1 { color: #002D62; font-family: 'Georgia', serif; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.balance = 1000000.0
    st.session_state.portfolio = {"Stocks": 0, "Bonds": 0, "Gold": 0}
    st.session_state.history = [1000000.0]
    st.session_state.prices = {"Stocks": 200.0, "Bonds": 100.0, "Gold": 1800.0}
    st.session_state.event = "Market Initialized. Awaiting Capital Allocation."

def next_turn():
    # Finance-specific events
    events = [
        {"msg": "Quantitative Easing: Equity markets surge on liquidity.", "stocks": 0.14, "bonds": 0.02, "gold": -0.04},
        {"msg": "Yield Curve Inversion: Recessional fears drive investors to Gold.", "stocks": -0.15, "bonds": 0.05, "gold": 0.12},
        {"msg": "Aggressive Rate Hike: Bond prices fall, Stock volatility increases.", "stocks": -0.10, "bonds": -0.07, "gold": -0.03},
        {"msg": "Positive Earnings Season: Corporate growth exceeds forecasts.", "stocks": 0.11, "bonds": 0.01, "gold": -0.06}
    ]
    selected_event = np.random.choice(events)
    st.session_state.event = selected_event["msg"]
    st.session_state.prices["Stocks"] *= (1 + selected_event["stocks"])
    st.session_state.prices["Bonds"] *= (1 + selected_event["bonds"])
    st.session_state.prices["Gold"] *= (1 + selected_event["gold"])
    
    current_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(current_val)
    st.session_state.step += 1

# Layout Header
st.title("🏛️ Investment Portfolio Management Simulator")
st.markdown("#### Finance Department | Advanced Decision-Making Lab")
st.divider()

# Top Metrics Bar
st.info(f"📅 **Trading Period:** {st.session_state.step} of 5 | 🏛 **Market Headline:** {st.session_state.event}")

m1, m2, m3 = st.columns(3)
m1.metric("Cash Balance (USD)", f"${st.session_state.balance:,.2f}")
m2.metric("AUM (Assets Under Management)", f"${st.session_state.history[-1]:,.2f}")
m3.metric("Completion Rate", f"{int(((st.session_state.step-1)/5)*100)}%")

# Main Logic
if st.session_state.step <= 5:
    st.write("### 📊 Portfolio Rebalancing & Allocation")
    with st.form("allocation_form"):
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Equities (Stocks) %", 0, 100, 0)
        b_pct = c2.slider("Fixed Income (Bonds) %", 0, 100, 0)
        g_pct = c3.slider("Commodities (Gold) %", 0, 100, 0)
        
        if st.form_submit_button("Confirm Trades & Execute Turn"):
            if s_pct + b_pct + g_pct > 100:
                st.error("Compliance Error: Allocation exceeds 100% of available capital.")
            else:
                total_w = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
                st.session_state.portfolio["Stocks"] = (total_w * (s_pct/100)) / st.session_state.prices["Stocks"]
                st.session_state.portfolio["Bonds"] = (total_w * (b_pct/100)) / st.session_state.prices["Bonds"]
                st.session_state.portfolio["Gold"] = (total_w * (g_pct/100)) / st.session_state.prices["Gold"]
                st.session_state.balance = total_w * (1 - (s_pct+b_pct+g_pct)/100)
                next_turn()
                st.rerun()
else:
    st.success("🏁 Portfolio Simulation Concluded.")
    final_v = st.session_state.history[-1]
    roi = ((final_v - 1000000)/1000000)*100
    
    # Performance Visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', name='Equity Curve', line=dict(color='#002D62', width=4)))
    fig.update_layout(title="Portfolio Equity Curve (Performance History)", xaxis_title="Round", yaxis_title="Total Value ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Financial Analytics Report
    st.write("### 📜 Final Financial Statement")
    report_df = pd.DataFrame({
        "Performance Metric": ["Final Portfolio Value", "Total Return (ROI %)", "Initial Capital"],
        "Value": [f"${final_v:,.2f}", f"{roi:.2f}%", "$1,000,000.00"]
    })
    st.table(report_df)
    
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        report_df.to_excel(wr, index=False, sheet_name='Performance_Analysis')
    st.download_button("📥 Export Performance Data (Excel)", data=buf.getvalue(), file_name="Finance_Simulation_Results.xlsx")
    
    if st.button("Initialize New Session"):
        st.session_state.clear()
        st.rerun()
