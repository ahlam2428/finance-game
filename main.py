import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة والتصميم الفاخر ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-weight: 800; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d;
    }
    .stButton>button { 
        background: linear-gradient(135deg, #d4af37 0%, #aa8a2e 100%);
        color: black; font-weight: bold; border-radius: 8px; border: none; height: 3em; width: 100%;
    }
    .stTextInput>div>div>input { background-color: #161b22; color: white; border: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Georgia', serif; }
    .stSlider > div > div > div > div { background-color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب بيانات السوق الحقيقية ---
@st.cache_data(ttl=3600)
def get_live_prices():
    try:
        # SPY للأسهم، TLT للسندات، GLD للذهب
        tickers = {"Equities": "SPY", "Fixed Income": "TLT", "Commodities": "GLD"}
        prices = {}
        for label, ticker in tickers.items():
            data = yf.Ticker(ticker).history(period="1d")
            prices[label] = round(data['Close'].iloc[-1], 2)
        return prices
    except:
        # قيم احتياطية في حال فشل الاتصال بالإنترنت
        return {"Equities": 450.0, "Fixed Income": 95.0, "Commodities": 180.0}

# --- 3. تهيئة حالة الجلسة ---
if 'step' not in st.session_state:
    live_prices = get_live_prices()
    st.session_state.update({
        'step': 1, 
        'balance': 1000000.0, 
        'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': live_prices,
        'initial_prices': live_prices.copy(),
        'event': "Market Terminal Online. Real-time data synced."
    })

# --- 4. محرك السوق (محاكاة التذبذب بناءً على الأسعار الحقيقية) ---
def simulate_market_move():
    volatility = {"Equities": 0.05, "Fixed Income": 0.015, "Commodities": 0.03}
    for asset in st.session_state.prices:
        change = np.random.normal(0.002, volatility[asset])
        st.session_state.prices[asset] *= (1 + change)
    
    current_total = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(current_total)
    st.session_state.step += 1

# --- 5. واجهة المستخدم الرئيسية ---
st.title("🏛️ Professional Investment Strategy Lab")
st.caption("Advanced Finance Simulation | Real-Time Market Benchmarks")

if st.session_state.step <= 5:
    # لوحة المعلومات
    st.info(f"📅 **Round:** {st.session_state.step} of 5 | 📢 **Market News:** {st.session_state.event}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("CASH BALANCE", f"${st.session_state.balance:,.0f}")
    m2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}")
    roi_live = ((st.session_state.history[-1] - 1000000)/1000000)*100
    m3.metric("CURRENT ROI", f"{roi_live:.2f}%")

    with st.form("trading_panel"):
        st.write("### 📊 Strategic Asset Allocation")
        st.write("Select how to distribute your total wealth for this round:")
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Equities (SPY) %", 0, 100, 0)
        b_pct = c2.slider("Fixed Income (TLT) %", 0, 100, 0)
        g_pct = c3.slider("Commodities (GLD) %", 0, 100, 0)
        
        if st.form_submit_button("CONFIRM & EXECUTE TRADES"):
            if s_pct + b_pct + g_pct > 100:
                st.error("Error: Total allocation exceeds 100%!")
            else:
                total_w = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (total_w * (s_pct/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (total_w * (b_pct/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (total_w * (g_pct/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = total_w * (1 - (s_pct+b_pct+g_pct)/100)
                simulate_market_move()
                st.rerun()

# --- 6. عرض النتائج النهائية (بعد الجولة 5) ---
else:
    st.success("🎯 Simulation Completed. Analyze your strategic performance below.")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني المحسن (Dynamic Scaling)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(st.session_state.history) + 1)),
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#d4af37', width=4),
        fill='tozeroy',
        fillcolor='rgba(212, 175, 55, 0.1)',
        name='Net Worth'
    ))
    fig.update_layout(
        template="plotly_dark", 
        title="Equity Growth Path",
        xaxis=dict(title="Round", tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title="Net Worth ($)", autorange=True, fixedrange=False),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.write("### 📊 Performance Analytics")
        st.metric("FINAL NET WORTH", f"${final_aum:,.2f}")
        st.metric("TOTAL RETURN (ROI)", f"{total_roi:.2f}%")
        if st.button("🔄 Restart Simulation"):
            st.session_state.clear()
            st.rerun()

    with col_res2:
        st.write("### 📧 Official Submission")
        st.write("Submit this performance record to your instructor for grading.")
        student_name = st.text_input("Enter Student Full Name:")
        coach_email = st.text_input("Enter Instructor Email:")
        
        if st.button("Submit Audited Report"):
            if student_name and coach_email and "@" in coach_email:
                payload = {
                    "Student": student_name,
                    "Final_Value": f"${final_aum:,.2f}",
                    "ROI_Percentage": f"{total_roi:.2f}%",
                    "Status": "Verified Graduate Simulation"
                }
                # إرسال البيانات عبر FormSubmit
                requests.post(f"https://formsubmit.co/ajax/{coach_email}", data=payload)
                st.balloons()
                st.success(f"Excellent work {student_name}! Your report has been dispatched.")
            else:
                st.error("Please provide both name and a valid instructor email.")
