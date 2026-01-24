import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. التصميم الملكي المظلم (High-End Dark UI) ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-weight: bold; font-size: 2.5rem !important; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; }
    h1, h2, h3, p, label { color: white !important; font-family: 'Arial'; }
    .stButton>button { 
        background-color: #0044CC; color: white; border-radius: 8px; font-weight: bold; 
        height: 3.5em; width: 100%; border: none; font-size: 1.1rem;
    }
    .stButton>button:hover { background-color: #00D1FF; color: black; }
    .stSlider > div > div > div > div { background-color: #00D1FF; }
    .stAlert { background-color: #161B22; border: 1px solid #00D1FF; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك جلب الأسعار ---
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
        return {"Equities": 490.0, "Fixed Income": 93.0, "Commodities": 180.0}

# --- 3. إدارة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "📢 System Online. Waiting for initial allocation..."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Tech Rally: High Demand for AI Stocks!", "e": 0.12, "f": -0.02, "c": -0.04},
        {"msg": "⚠️ Geopolitical Tension: Gold becomes a safe haven.", "e": -0.07, "f": 0.04, "c": 0.15},
        {"msg": "🏦 Central Bank: Interest rate hike announced.", "e": -0.05, "f": -0.10, "c": -0.02}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. العرض الرئيسي ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | News: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH", f"${st.session_state.balance:,.0f}")
    col2.metric("TOTAL PORTFOLIO", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("ROI %", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.write("### 🛠️ Strategic Asset Allocation")
        s = st.slider("Equities (SPY) %", 0, 100, 40)
        b = st.slider("Bonds (TLT) %", 0, 100, 30)
        g = st.slider("Gold (GLD) %", 0, 100, 30)
        
        if st.form_submit_button("EXECUTE STRATEGY"):
            if s + b + g > 100:
                st.error("❌ Allocation exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. صفحة النتائج (تم إصلاح خطأ fig و الإرسال) ---
else:
    st.success("🎯 Simulation Completed Successfully!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # 1. إنشاء الرسم البياني أولاً لتجنب الـ NameError
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#00D1FF', width=4),
        fill='tozeroy'
    ))
    fig.update_layout(
        title="Portfolio Growth Path",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Round"),
        yaxis=dict(title="Value ($)")
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.write("### 📈 Summary Statistics")
        st.metric("FINAL NET WORTH", f"${final_aum:,.2f}")
        st.metric("TOTAL RETURN", f"{total_roi:.2f}%")
        if st.button("🔄 Restart Simulation"):
            st.session_state.clear()
            st.rerun()

    with c2:
        st.write("### 📧 Instructor Verified Submission")
        s_name = st.text_input("Student Name:")
        i_email = st.text_input("Instructor Email:")
        
        if s_name and i_email and "@" in i_email:
            # طريقة الإرسال المضمونة (رابط مباشر) لضمان عدم الفشل
            report_msg = f"Student: {s_name} | Final Value: ${final_aum:,.2f} | ROI: {total_roi:.2f}%"
            form_url = f"https://formsubmit.co/{i_email}?subject=Lab_Result_{s_name}&text={report_msg}"
            
            st.markdown(f'''
                <a href="{form_url}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #00D1FF; color: black; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; cursor: pointer;">
                        🚀 CLICK HERE TO FINALIZE & SEND TO INSTRUCTOR
                    </div>
                </a>
            ''', unsafe_allow_html=True)
            st.caption("Clicking the button above will open a secure window to confirm your submission.")
        else:
            st.warning("Please enter a valid Name and Email to enable submission.")
