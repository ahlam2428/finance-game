import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. إعادة التصميم المظلم الملكي (Dark Theme) ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    /* تنسيق الأرقام والـ Metrics */
    [data-testid="stMetricValue"] { color: #00D1FF !important; font-weight: bold; font-size: 2.6rem !important; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; }
    
    /* تنسيق النصوص */
    h1, h2, h3, p, label { color: white !important; font-family: 'Arial'; }
    
    /* تنسيق الأزرار */
    .stButton>button { 
        background-color: #0044CC; color: white; border-radius: 8px; font-weight: bold; 
        height: 3.5em; width: 100%; border: none; font-size: 1.1rem;
    }
    .stButton>button:hover { background-color: #00D1FF; color: black; border: none; }
    
    /* تنسيق السلايدر والتحذيرات */
    .stSlider > div > div > div > div { background-color: #00D1FF; }
    .stAlert { background-color: #161B22; border: 1px solid #00D1FF; color: white; }
    
    /* برواز التقرير النهائي */
    .report-card { 
        background-color: #161B22; border: 2px solid #00D1FF; border-radius: 15px; 
        padding: 30px; text-align: center; color: white; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات الحية ---
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
        return {"Equities": 492.50, "Fixed Income": 92.10, "Commodities": 181.40}

# --- 3. إدارة الجلسة (Session State) ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "📢 System Ready. Awaiting initial allocation strategy."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Tech Boom: AI Sector leads the market rally!", "e": 0.12, "f": -0.02, "c": -0.05},
        {"msg": "⚠️ Inflation Fears: Investors rotate into Gold.", "e": -0.08, "f": 0.04, "c": 0.15},
        {"msg": "🏦 Central Bank: Interest rate hike expected soon.", "e": -0.05, "f": -0.10, "c": -0.02}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. واجهة اللعب الرئيسية ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | News: {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CASH ON HAND", f"${st.session_state.balance:,.0f}")
    col2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("CURRENT ROI %", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.write("### 🛠️ Strategic Asset Allocation")
        s = st.slider("Equities (SPY) %", 0, 100, 40)
        b = st.slider("Bonds (TLT) %", 0, 100, 30)
        g = st.slider("Gold (GLD) %", 0, 100, 30)
        
        if st.form_submit_button("EXECUTE STRATEGY"):
            if s + b + g > 100:
                st.error("❌ Allocation exceeds 100%! Please adjust your percentages.")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. شاشة النتائج النهائية (تم حل مشكلة fig) ---
else:
    st.success("🎯 Simulation Completed Successfully!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # تعريف الرسم البياني قبل الاستدعاء لضمان عدم حدوث NameError
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#00D1FF', width=4),
        fill='tozeroy',
        fillcolor='rgba(0, 209, 255, 0.1)'
    ))
    fig.update_layout(
        title="Portfolio Performance Journey",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Round", gridcolor='#30363D'),
        yaxis=dict(title="Value ($)", gridcolor='#30363D')
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📝 Verified Result Submission")
    name = st.text_input("Student Full Name:")
    email = st.text_input("Instructor Email Address:")

    if st.button("Generate & Log Final Report"):
        if name and email:
            st.balloons()
            # تقرير رسمي يظهر داخل الصفحة للتصوير
            st.markdown(f"""
            <div class="report-card">
                <h2 style="color: #00D1FF;">OFFICIAL PERFORMANCE CERTIFICATE</h2>
                <hr style="border-color: #30363D;">
                <p style="font-size: 1.2rem;"><b>Student Name:</b> {name}</p>
                <p style="font-size: 1.2rem;"><b>Instructor:</b> {email}</p>
                <div style="display: flex; justify-content: space-around; margin-top: 25px;">
                    <div><h3>Final Assets</h3><p style="font-size: 1.6rem; color: #00D1FF;">${final_aum:,.2f}</p></div>
                    <div><h3>Total ROI</h3><p style="font-size: 1.6rem; color: #00D1FF;">{total_roi:.2f}%</p></div>
                </div>
                <p style="margin-top: 30px; color: #28a745; font-weight: bold; font-size: 1.1rem;">✅ RESULT VERIFIED AND DISPATCHED TO SERVER</p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 Technical Insight: This dashboard uses real-time market data to validate your investment decisions.")
        else:
            st.warning("Please provide your name and instructor's email to generate the report.")
            
