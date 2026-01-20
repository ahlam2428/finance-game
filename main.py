import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات التصميم (عالي الوضوح - فاتح) ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: 900; font-size: 2.8rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; padding: 25px; border-radius: 12px; border: 2px solid #DEE2E6;
    }
    h1, h2, h3, h4, p, label { color: #000000 !important; font-weight: bold !important; }
    .stButton>button { 
        background-color: #0044CC; color: #FFFFFF; border-radius: 8px; font-weight: 900; 
        height: 3.5em; width: 100%; font-size: 1.2rem;
    }
    .stSlider > div > div > div > div { background-color: #0044CC; }
    .stAlert { background-color: #E7F0FF; color: #000000; border: 1px solid #0044CC; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب بيانات السوق (الأساس) ---
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
        'prices': live_prices,
        'event': "📢 Welcome, Trader. Deploy your capital to begin."
    })

# --- 4. محرك الأخبار العشوائية وتأثيرها على السوق ---
def process_turn():
    # قائمة الأخبار وتأثيرها (Multiplier) على الأسعار الحقيقية
    scenarios = [
        {"msg": "🚀 AI BREAKTHROUGH: Tech sector leads a massive market rally!", "e": 0.12, "f": 0.01, "c": -0.05},
        {"msg": "⚠️ GEOPOLITICAL TENSION: Investors rush to Gold as a safe haven.", "e": -0.08, "f": 0.04, "c": 0.15},
        {"msg": "🏦 CENTRAL BANK ACTION: Unexpected rate hikes crash bond prices.", "e": -0.05, "f": -0.12, "c": -0.02},
        {"msg": "📉 GLOBAL RECESSION FEARS: Consumer spending drops sharply.", "e": -0.15, "f": 0.06, "c": 0.08},
        {"msg": "⚡ ENERGY CRISIS: Oil and Commodity prices skyrocket.", "e": -0.04, "f": -0.02, "c": 0.18}
    ]
    
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    
    # تحديث الأسعار بناءً على الخبر
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    # حساب القيمة الإجمالية
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 5. الواجهة الرئيسية ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    # عرض الخبر بشكل بارز جداً
    st.info(f"📅 Round: {st.session_state.step} of 5 | {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("AVAILABLE CASH", f"${st.session_state.balance:,.0f}")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI", f"{roi:.2f}%")

    with st.form("trading_panel"):
        st.write("### 🛠️ Portfolio Allocation")
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Equities (Stocks) %", 0, 100, 0)
        b_pct = c2.slider("Fixed Income (Bonds) %", 0, 100, 0)
        g_pct = c3.slider("Commodities (Gold) %", 0, 100, 0)
        
        if st.form_submit_button("EXECUTE TRADES"):
            if s_pct + b_pct + g_pct > 100:
                st.error("Error: Total allocation cannot exceed 100%.")
            else:
                current_w = st.session_state.history[-1]
                # توزيع المحفظة
                st.session_state.portfolio["Equities"] = (current_w * (s_pct/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (current_w * (b_pct/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (current_w * (g_pct/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = current_w * (1 - (s_pct+b_pct+g_pct)/100)
                process_turn()
                st.rerun()

# --- 6. عرض النتائج النهائية والرسم البياني المحسن ---
else:
    st.success("🎯 Simulation Completed. Review your results below.")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني عالي الوضوح
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history))), 
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#0044CC', width=5),
        marker=dict(size=10, color='#0044CC'),
        fill='tozeroy',
        fillcolor='rgba(0, 68, 204, 0.1)'
    ))
    fig.update_layout(
        title="Portfolio Value History",
        xaxis=dict(title="Round", tickmode='linear', dtick=1, gridcolor='#EEEEEE'),
        yaxis=dict(title="Value ($)", autorange=True, gridcolor='#EEEEEE'),
        plot_bgcolor='white', paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.metric("FINAL VALUE", f"${final_aum:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart & Try Again"):
            st.session_state.clear()
            st.rerun()
    
    with c_res2:
        st.write("### 📧 Send Audited Results")
        s_name = st.text_input("Enter Your Full Name:")
        i_email = st.text_input("Instructor Email Address:")
        if st.button("Submit Report"):
            if s_name and "@" in i_email:
                data = {"Student": s_name, "Final_AUM": f"${final_aum:,.2f}", "ROI": f"{total_roi:.2f}%"}
                requests.post(f"https://formsubmit.co/ajax/{i_email}", data=data)
                st.balloons()
                st.success("Your performance report has been sent.")
