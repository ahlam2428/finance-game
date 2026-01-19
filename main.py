import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="Strategic Investment Simulator", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E3A8A; color: white; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.balance = 1000000.0
    st.session_state.portfolio = {"Stocks": 0, "Bonds": 0, "Gold": 0}
    st.session_state.history = [1000000.0]
    st.session_state.prices = {"Stocks": 200.0, "Bonds": 100.0, "Gold": 1800.0}
    st.session_state.event = "Game Started: Allocate your capital wisely."

# Market Logic Engine
def next_turn():
    events = [
        {"msg": "Central Bank raises interest rates to combat inflation!", "stocks": -0.12, "bonds": -0.06, "gold": -0.03},
        {"msg": "Tech breakthrough leads to a massive market rally.", "stocks": 0.18, "bonds": 0.01, "gold": -0.07},
        {"msg": "Geopolitical tensions increase; investors flock to safe havens.", "stocks": -0.15, "bonds": 0.04, "gold": 0.12},
        {"msg": "Global energy crisis hits production costs.", "stocks": -0.08, "bonds": -0.02, "gold": 0.05},
        {"msg": "Economic growth exceeds expectations; consumer confidence is high.", "stocks": 0.10, "bonds": 0.03, "gold": -0.04}
    ]
    
    selected_event = np.random.choice(events)
    st.session_state.event = selected_event["msg"]
    
    # Update Asset Prices based on the event
    st.session_state.prices["Stocks"] *= (1 + selected_event["stocks"])
    st.session_state.prices["Bonds"] *= (1 + selected_event["bonds"])
    st.session_state.prices["Gold"] *= (1 + selected_event["gold"])
    
    # Calculate Total Portfolio Value
    current_value = st.session_state.balance
    for asset, qty in st.session_state.portfolio.items():
        current_value += qty * st.session_state.prices[asset]
    
    st.session_state.history.append(current_value)
    st.session_state.step += 1

# Header Section
st.title("📊 Strategic Investment Simulator")
st.subheader("Master's Level Financial Decision-Making Tool")
st.divider()

# Dashboard Metrics
st.info(f"📅 **Round:** {st.session_state.step} of 5 | 📢 **Market News:** {st.session_state.event}")

m1, m2, m3 = st.columns(3)
m1.metric("Cash Liquidity", f"${st.session_state.balance:,.2f}")
m2.metric("Total Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
m3.metric("Step Progress", f"{st.session_state.step}/5")

# Game Phase
if st.session_state.step <= 5:
    st.write("### 🛠 Portfolio Management")
    with st.form("trade_form"):
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Stocks Allocation (%)", 0, 100, 0)
        b_pct = c2.slider("Bonds Allocation (%)", 0, 100, 0)
        g_pct = c3.slider("Gold Allocation (%)", 0, 100, 0)
        
        submit = st.form_submit_button("Execute Strategy & Next Round")
        
        if submit:
            if s_pct + b_pct + g_pct > 100:
                st.error("Invalid Allocation: Total percentage exceeds 100%!")
            else:
                # Rebalance Portfolio
                total_wealth = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
                st.session_state.portfolio["Stocks"] = (total_wealth * (s_pct/100)) / st.session_state.prices["Stocks"]
                st.session_state.portfolio["Bonds"] = (total_wealth * (b_pct/100)) / st.session_state.prices["Bonds"]
                st.session_state.portfolio["Gold"] = (total_wealth * (g_pct/100)) / st.session_state.prices["Gold"]
                st.session_state.balance = total_wealth * (1 - (s_pct+b_pct+g_pct)/100)
                next_turn()
                st.rerun()

# Results Phase
else:
    st.success("🎯 Simulation Complete! Review the Financial Performance Analysis below.")
    
    final_val = st.session_state.history[-1]
    roi = ((final_val - 1000000) / 1000000) * 100
    volatility = np.std(st.session_state.history)
    sharpe = (roi / (volatility/10000)) if volatility != 0 else 0

    r1, r2, r3 = st.columns(3)
    r1.metric("Final ROI", f"{roi:.2f}%")
    r2.metric("Risk Level (Volatility)", f"{volatility:,.0f}")
    r3.metric("Efficiency (Sharpe Ratio)", f"{sharpe:.2f}")

    # Performance Graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#1E3A8A', width=4)))
    fig.update_layout(title="Portfolio Equity Curve", xaxis_title="Round", yaxis_title="Net Worth ($)")
    st.plotly_chart(fig, use_container_width=True)

    # Excel Report for Instructor
    report_df = pd.DataFrame({
        "Metric": ["Final Net Worth", "Total ROI (%)", "Volatility", "Sharpe Ratio"],
        "Result": [f"${final_val:,.2f}", f"{roi:.2f}%", round(volatility, 2), round(sharpe, 2)]
    })
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Performance_Report')
    
    st.download_button(
        label="📥 Download Performance Report (Excel)",
        data=buffer.getvalue(),
        file_name="student_assessment.xlsx",
        mime="application/vnd.ms-excel"
    )

    if st.button("Restart Simulation"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
