import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات الصفحة والتصميم (High-Contrast Light Theme) ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    /* خلفية بيضاء وخطوط سوداء واضحة */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* تنسيق بطاقات الأرقام (خلفية فاتحة وحدود واضحة) */
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: 900; font-size: 2.8rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        padding: 25px; 
        border-radius: 12px; 
        border: 2px solid #DEE2E6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* نصوص العناوين سوداء تماماً وواضحة */
    h1, h2, h3, h4, p, label { 
        color: #000000 !important; 
        font-family: 'Arial', sans-serif; 
        font-weight: bold !important;
    }

    /* تنسيق الأزرار (أزرق ملكي مع خط أبيض عريض) */
    .stButton>button { 
        background-color: #0044CC; 
        color: #FFFFFF; 
        border-radius: 8px; 
        font-weight: 900; 
        border: none; 
        height: 3.5em; 
        width: 100%; 
        font-size: 1.2rem;
    }
    .stButton>button:hover { background-color: #003399; color: #FFFFFF; }

    /* تحسين وضوح السلايدر (المزلاق) */
    .stSlider > div > div > div > div { background-color: #0044CC; }
    
    /* تنسيق صناديق التنبيه */
    .stAlert { background-color: #E7F0FF; color: #000000; border: 1px solid #0044CC; }
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
        'prices': live_prices, 'event': "Market Terminal Ready. Live data connected."
    })

def simulate_market_move():
    vol = {"Equities": 0.05, "Fixed Income": 0.015, "Commodities": 0.03}
    for asset in st.session_state.prices:
        change = np.random.normal(0.002, vol[asset])
        st.session_state.prices[asset] *= (1 + change)
    
    val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(val)
    st.session_state.step += 1

# --- 4. واجهة المستخدم ---
st.title("🏛️ Portfolio Strategy Simulation")
st.write("Professional Decision Support Tool for Finance Students")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | 📢 Status: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("AVAILABLE CASH", f"${st.session_state.balance:,.0f}")
    col2.metric("PORTFOLIO VALUE", f"${st.session_state.history[-1]:,.0f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.subheader("🛠️ Portfolio Rebalancing")
        c1, c2, c3 = st.columns(3)
        s = c1.slider("Equities (SPY) %", 0, 100, 0)
        b = c2.slider("Fixed Income (TLT) %", 0, 100, 0)
        g = c3.slider("Commodities (GLD) %", 0, 100, 0)
        
        if st.form_submit_button("CONFIRM ALLOCATION"):
            if s + b + g > 100:
                st.error("Error: Total allocation cannot exceed 100%!")
            else:
                total_w = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (total_w * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (total_w * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (total_w * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = total_w * (1 - (s+b+g)/100)
                simulate_market_move()
                st.rerun()

# --- 5. النتائج النهائية والرسم البياني الواضح ---
else:
    st.success("🎯 Simulation Completed.")
    final_val = st.session_state.history[-1]
    total_roi = ((final_val - 1000000)/1000000)*100
    
    # رسم بياني بخلفية بيضاء وخطوط واضحة جداً
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history))), 
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#0044CC', width=6),
        marker=dict(size=12, color='#0044CC'),
        name='Portfolio Value'
    ))
    fig.update_layout(
        title=dict(text="Investment Performance History", font=dict(size=24, color='black')),
        xaxis=dict(title="Trading Round", tickmode='linear', dtick=1, gridcolor='#E5E5E5', tickfont=dict(color='black', size=14)),
        yaxis=dict(title="Value ($)", autorange=True, gridcolor='#E5E5E5', tickfont=dict(color='black', size=14)),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.write("### 📊 Summary Statistics")
        st.metric("FINAL VALUE", f"${final_val:,.2f}")
        st.metric("NET RETURN", f"{total_roi:.2f}%")
        if st.button("🔄 Restart Game"):
            st.session_state.clear()
            st.rerun()
    
    with c_res2:
        st.write("### 📧 Instructor Submission")
        name = st.text_input("Student Full Name:")
        email = st.text_input("Instructor Email:")
        if st.button("Submit My Results"):
            if name and "@" in email:
                requests.post(f"https://formsubmit.co/ajax/{email}", data={"Student": name, "ROI": f"{total_roi:.2f}%", "AUM": f"${final_val:,.2f}"})
                st.balloons()
                st.success("Report sent successfully!")
