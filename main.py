import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests

# --- 1. إعدادات التصميم (عالية الوضوح - فاتح) ---
st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stMetricValue"] { color: #0044CC !important; font-weight: 900; font-size: 2.8rem !important; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; padding: 20px; border-radius: 12px; border: 2px solid #DEE2E6;
    }
    h1, h2, h3, h4, p, label { color: #000000 !important; font-weight: bold !important; font-family: 'Arial'; }
    .stButton>button { 
        background-color: #0044CC; color: #FFFFFF; border-radius: 8px; font-weight: 900; 
        height: 3.5em; width: 100%; font-size: 1.2rem; border: none;
    }
    .stButton>button:hover { background-color: #003399; color: #FFFFFF; border: 1px solid #0044CC; }
    .stSlider > div > div > div > div { background-color: #0044CC; }
    .stAlert { background-color: #E7F0FF; color: #000000; border: 1px solid #0044CC; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب بيانات السوق الحية ---
@st.cache_data(ttl=3600)
def get_live_prices():
    try:
        # أسهم أمريكية (SPY)، سندات (TLT)، ذهب (GLD)
        tickers = {"Equities": "SPY", "Fixed Income": "TLT", "Commodities": "GLD"}
        prices = {}
        for label, ticker in tickers.items():
            data = yf.Ticker(ticker).history(period="1d")
            prices[label] = round(data['Close'].iloc[-1], 2)
        return prices
    except:
        # أسعار احتياطية في حال تعطل الاتصال
        return {"Equities": 480.0, "Fixed Income": 95.0, "Commodities": 185.0}

# --- 3. تهيئة حالة الجلسة ---
if 'step' not in st.session_state:
    live_prices = get_live_prices()
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': live_prices,
        'event': "📢 System Ready. Welcome to the Investment Simulation."
    })

# --- 4. محرك الأخبار والتحولات ---
def process_turn():
    scenarios = [
        {"msg": "🚀 TECH RALLY: AI breakthrough boosts Equity markets!", "e": 0.12, "f": -0.02, "c": -0.04},
        {"msg": "⚠️ MARKET VOLATILITY: Investors move to Gold as a safe haven.", "e": -0.08, "f": 0.04, "c": 0.15},
        {"msg": "🏦 RATE HIKE: Central banks raise rates; Bond prices fall.", "e": -0.05, "f": -0.10, "c": -0.02},
        {"msg": "📉 RECESSION FEARS: Global demand slows down.", "e": -0.15, "f": 0.07, "c": 0.05},
        {"msg": "🔥 COMMODITY SPIKE: Oil & Gold prices jump amid supply risks.", "e": -0.04, "f": -0.03, "c": 0.18}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    # حساب القيمة الإجمالية للمحفظة بعد الجولة
    current_assets_val = sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    total_val = st.session_state.balance + current_assets_val
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 5. واجهة اللعبة الرئيسية ---
st.title("🏛️ Global Markets Simulation Terminal")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | News: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH ON HAND", f"${st.session_state.balance:,.0f}", help="Total cash not yet invested.")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.0f}", help="Sum of cash and market value of your assets.")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI %", f"{roi:.2f}%", help="Performance relative to starting $1M.")

    with st.form("trade_form"):
        st.write("### 🛠️ Strategic Asset Allocation")
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("Equities (Stocks) %", 0, 100, 0, help="Growth assets (SPY ETF).")
        b_pct = c2.slider("Fixed Income (Bonds) %", 0, 100, 0, help="Defensive assets (TLT ETF).")
        g_pct = c3.slider("Commodities (Gold) %", 0, 100, 0, help="Inflation hedge (GLD ETF).")
        
        if st.form_submit_button("EXECUTE ALLOCATION"):
            if s_pct + b_pct + g_pct > 100:
                st.error("❌ Allocation total exceeds 100%. Please adjust.")
            else:
                current_total = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (current_total * (s_pct/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (current_total * (b_pct/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (current_total * (g_pct/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = current_total * (1 - (s_pct+b_pct+g_pct)/100)
                process_turn()
                st.rerun()

# --- 6. صفحة النتائج النهائية ونظام الإرسال ---
else:
    st.success("🎯 Simulation Completed! Analyzing your results...")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني للأداء
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(st.session_state.history))), 
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#0044CC', width=4),
        fill='tozeroy', fillcolor='rgba(0, 68, 204, 0.1)'
    ))
    fig.update_layout(title="Portfolio Growth Journey", xaxis_title="Round", yaxis_title="Net Value ($)", plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    res1, res2 = st.columns(2)
    with res1:
        st.write("### 📈 Performance Summary")
        st.metric("FINAL VALUE", f"${final_aum:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Try Again (Reset)"):
            st.session_state.clear()
            st.rerun()

    with res2:
        st.write("### 📧 Official Result Submission")
        st.write("Instructor receives a verified performance table.")
        name = st.text_input("Student Full Name:")
        email = st.text_input("Instructor Email Address:")
        
        if st.button("Submit Audited Report"):
            if name and email and "@" in email:
                try:
                    # البيانات المرسلة للخدمة
                    payload = {
                        "Student_Name": name,
                        "Final_AUM": f"${final_aum:,.2f}",
                        "Total_ROI": f"{total_roi:.2f}%",
                        "_subject": f"Investment Lab Report: {name}",
                        "_captcha": "false", # تخطي اختبار الروبوت للسرعة
                        "_template": "table" # شكل الإيميل يكون جدول
                    }
                    # الإرسال المباشر
                    response = requests.post(f"https://formsubmit.co/{email}", data=payload)
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success(f"Report sent to {email}")
                        st.info("💡 TIP: If this is the first report, the instructor must click 'Activate' in the confirmation email.")
                    else:
                        st.error("System Busy. Please try again.")
                except:
                    st.error("Connection failed. Check your internet.")
            else:
                st.warning("Please provide both name and valid email.")
                
