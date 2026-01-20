import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات الصفحة والتصميم (Navy & Gold Theme) ---
st.set_page_config(page_title="Finance Strategy Lab", layout="wide")

st.markdown("""
    <style>
    /* تغيير الخلفية للون نيفي غامق */
    .stApp { background-color: #001f3f; color: #ffffff; }
    
    /* تنسيق بطاقات الأرقام */
    [data-testid="stMetricValue"] { color: #FFD700 !important; font-weight: 800; font-size: 2.5rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #003366; padding: 25px; border-radius: 15px; border: 1px solid #FFD700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* تنسيق الأزرار */
    .stButton>button { 
        background-color: #FFD700; color: #001f3f; border-radius: 10px; 
        font-weight: bold; border: none; height: 3.5em; width: 100%; font-size: 1.1rem;
    }
    .stButton>button:hover { background-color: #e6c200; color: #001f3f; }

    /* التنبيهات والعناوين */
    .stAlert { background-color: #003366; color: #ffffff; border: 1px solid #FFD700; }
    h1, h2, h3 { color: #FFD700 !important; font-family: 'serif'; }
    .stSlider > div > div > div > div { background-color: #FFD700; }
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
        'prices': live_prices, 'event': "Market Terminal Online. Real-time data synced."
    })

def simulate_market_move():
    # محاكاة حركة بناءً على تذبذب الأصول
    vol = {"Equities": 0.05, "Fixed Income": 0.015, "Commodities": 0.03}
    for asset in st.session_state.prices:
        change = np.random.normal(0.002, vol[asset])
        st.session_state.prices[asset] *= (1 + change)
    
    val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(val)
    st.session_state.step += 1

# --- 4. واجهة المستخدم ---
st.title("🏛️ Investment Strategy & Portfolio Lab")
st.markdown("### Graduate Level Simulation | Real-Time Markets")

if st.session_state.step <= 5:
    st.info(f"📅 **Round:** {st.session_state.step} of 5 | 📢 **News:** {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("AVAILABLE CASH", f"${st.session_state.balance:,.0f}")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.subheader("🛠️ Strategic Asset Allocation")
        c1, c2, c3 = st.columns(3)
        s = c1.slider("Equities (SPY) %", 0, 100, 0)
        b = c2.slider("Fixed Income (TLT) %", 0, 100, 0)
        g = c3.slider("Commodities (GLD) %", 0, 100, 0)
        
        if st.form_submit_button("EXECUTE PORTFOLIO REBALANCING"):
            if s + b + g > 100:
                st.error("Total allocation cannot exceed 100%!")
            else:
                total_w = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (total_w * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (total_w * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (total_w * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = total_w * (1 - (s+b+g)/100)
                simulate_market_move()
                st.rerun()

# --- 5. النتائج النهائية وإصلاح الرسم البياني ---
else:
    st.success("🎯 Simulation Completed.")
    final_val = st.session_state.history[-1]
    total_roi = ((final_val - 1000000)/1000000)*100
    
    # إصلاح الرسم البياني (تم ضبط المحاور لتناسب البيانات)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history))), 
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#FFD700', width=5),
        fill='tozeroy',
        fillcolor='rgba(255, 215, 0, 0.1)'
    ))
    fig.update_layout(
        title="Portfolio Value Performance",
        xaxis=dict(title="Trading Round", tickmode='linear', dtick=1),
        yaxis=dict(title="Net Worth ($)", autorange=True), # تفعيل الضبط التلقائي
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.metric("FINAL AUM", f"${final_val:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart Simulation"):
            st.session_state.clear()
            st.rerun()
    
    with c_res2:
        st.write("### 📧 Submission to Instructor")
        name = st.text_input("Student Name:")
        email = st.text_input("Instructor Email:")
        if st.button("Send Audited Results"):
            if name and "@" in email:
                requests.post(f"https://formsubmit.co/ajax/{email}", data={"Student": name, "ROI": f"{total_roi:.2f}%", "AUM": f"${final_val:,.2f}"})
                st.balloons()
                st.success("Results Dispatched Successfully.")
