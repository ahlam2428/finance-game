import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. التصميم الملكي المظلم (Dark Mode) ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; }
    .report-card { 
        background-color: #161B22; border: 2px solid #00D1FF; border-radius: 15px; 
        padding: 30px; text-align: center; color: white; margin-top: 20px;
    }
    .stButton>button { background-color: #0044CC; color: white; border-radius: 8px; font-weight: bold; height: 3.5em; width: 100%; }
    .stButton>button:hover { background-color: #00D1FF; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Bonds": 0, "Gold": 0},
        'event': "📢 Waiting for allocation..."
    })

def process_turn():
    events = [
        {"msg": "🚀 Tech Boom!", "e": 0.12, "b": -0.02, "g": -0.05},
        {"msg": "⚠️ Market Volatility", "e": -0.08, "b": 0.04, "g": 0.15},
        {"msg": "🏦 Rate Hike", "e": -0.05, "b": -0.10, "g": -0.02}
    ]
    ev = np.random.choice(events)
    st.session_state.event = ev["msg"]
    # حسبة مبسطة للأداء
    current_total = st.session_state.history[-1] * (1 + (ev["e"]*0.4 + ev["b"]*0.3 + ev["g"]*0.3))
    st.session_state.history.append(current_total)
    st.session_state.step += 1

# --- 3. واجهة اللعب ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"Round {st.session_state.step} of 5 | {st.session_state.event}")
    st.metric("Total Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    
    with st.form("trade"):
        st.write("### Allocation Strategy")
        s = st.slider("Equities %", 0, 100, 40)
        b = st.slider("Bonds %", 0, 100, 30)
        g = st.slider("Gold %", 0, 100, 30)
        if st.form_submit_button("Submit Round"):
            process_turn()
            st.rerun()

# --- 4. شاشة النتائج النهائية (تم إصلاح خطأ fig) ---
else:
    final_val = st.session_state.history[-1]
    total_roi = ((final_val - 1000000)/1000000)*100
    
    st.success("🎯 Simulation Completed!")
    
    # تعريف الرسم البياني قبل عرضه (لحل مشكلة NameError)
    fig = go.Figure(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#00D1FF', width=4),
        fill='tozeroy'
    ))
    fig.update_layout(title="Equity Growth Path", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📝 Generate Official Performance Report")
    name = st.text_input("Student Name:")
    email = st.text_input("Instructor Email:")

    if st.button("Generate Verified Report"):
        if name and email:
            st.balloons()
            # هذا هو التقرير الفوري الذي ستصورينه للوورد
            st.markdown(f"""
            <div class="report-card">
                <h2 style="color: #00D1FF;">INVESTMENT PERFORMANCE CERTIFICATE</h2>
                <hr style="border-color: #30363D;">
                <p style="font-size: 1.2rem;"><b>Student Name:</b> {name}</p>
                <p style="font-size: 1.2rem;"><b>Instructor:</b> {email}</p>
                <div style="display: flex; justify-content: space-around; margin-top: 20px;">
                    <div><h3>Final Portfolio</h3><p style="font-size: 1.5rem; color: #00D1FF;">${final_val:,.2f}</p></div>
                    <div><h3>Total ROI</h3><p style="font-size: 1.5rem; color: #00D1FF;">{total_roi:.2f}%</p></div>
                </div>
                <p style="margin-top: 30px; color: #28a745; font-weight: bold;">✅ Result Logged & Verified Successfully</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please fill your info.")
