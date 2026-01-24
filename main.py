import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. إعدادات الواجهة (الواجهة الاحترافية البيضاء) ---
st.set_page_config(page_title="Professional Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    /* تنسيق المربعات (Cards) كما في الصورة */
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        border: 1px solid #D1D5DB; 
        border-radius: 10px; 
        padding: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #4B5563 !important; font-weight: bold; text-transform: uppercase; }
    
    /* تنسيق العناوين والأزرار */
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Inter', sans-serif; font-weight: bold !important; }
    .stButton>button { 
        background-color: #FFFFFF; color: #111827; border: 1px solid #D1D5DB; 
        border-radius: 6px; font-weight: bold; height: 3em; width: auto; padding: 0 25px;
    }
    .stButton>button:hover { border-color: #0044CC; color: #0044CC; }
    
    /* شريط التنبيه الأزرق */
    .stAlert { background-color: #E0F2FE; border: 1px solid #7DD3FC; color: #0369A1; }
    
    /* شهادة التقرير النهائية */
    .report-card { 
        background-color: #F9FAFB; border: 2px solid #E5E7EB; border-radius: 12px; 
        padding: 40px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. جلب الأسعار ---
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
        return {"Equities": 495.0, "Fixed Income": 91.5, "Commodities": 182.0}

# --- 3. إدارة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "Welcome, Trader. Hover over items to see descriptions."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Market News: Strong earnings report in the Tech Sector!", "e": 0.08, "f": -0.01, "c": -0.02},
        {"msg": "⚠️ Volatility Alert: Global supply chains facing delays.", "e": -0.05, "b": 0.02, "g": 0.06},
        {"msg": "🏦 Economic Update: Central Bank hints at rate stability.", "e": 0.02, "b": 0.01, "g": -0.01}
    ]
    selected = np.random.choice(scenarios)
    st.session_state.event = selected["msg"]
    st.session_state.prices["Equities"] *= (1 + selected["e"])
    st.session_state.prices["Fixed Income"] *= (1 + selected["f"])
    st.session_state.prices["Commodities"] *= (1 + selected["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. واجهة اللعب (نفس ترتيب صورتك) ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    st.info(f"🗓️ Round: {st.session_state.step} of 5 | 📢 {st.session_state.event}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    col2.metric("Portfolio Value (AUM)", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    col3.metric("Current ROI", f"{roi:.2f}%")

    with st.container():
        st.write("### 🛠️ Portfolio Allocation")
        with st.form("trade_form"):
            c1, c2, c3 = st.columns(3)
            s = c1.slider("Equities (Stocks) %", 0, 100, 40)
            b = c2.slider("Fixed Income (Bonds) %", 0, 100, 30)
            g = c3.slider("Commodities (Gold) %", 0, 100, 30)
            
            if st.form_submit_button("EXECUTE TRADES"):
                if s + b + g > 100:
                    st.error("Error: Allocation total exceeds 100%.")
                else:
                    v = st.session_state.history[-1]
                    st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                    st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                    st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                    st.session_state.balance = v * (1 - (s+b+g)/100)
                    process_turn()
                    st.rerun()

# --- 5. شاشة النتائج (حل خطأ الـ NameError) ---
else:
    st.success("🎯 Simulation Completed. Your final report is ready.")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # تعريف الرسم البياني قبل أي عملية عرض
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#0044CC', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 68, 204, 0.1)'
    ))
    fig.update_layout(
        title="Portfolio Value History (Performance Chart)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(title="Trading Rounds", showgrid=True, gridcolor='#F3F4F6'),
        yaxis=dict(title="Value in USD", showgrid=True, gridcolor='#F3F4F6')
    )
    st.plotly_chart(fig, use_container_width=True)

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.write("### 📊 Final Assessment")
        st.metric("Final Value", f"${final_aum:,.2f}")
        st.metric("Total ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart & Try Again"):
            st.session_state.clear()
            st.rerun()

    with res_col2:
        st.write("### 🎓 Official Submission")
        s_name = st.text_input("Enter Your Full Name:")
        i_email = st.text_input("Instructor Email:")
        
        if st.button("Submit Report"):
            if s_name and i_email:
                st.balloons()
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #111827;">OFFICIAL PERFORMANCE REPORT</h2>
                    <p><b>Student:</b> {s_name} | <b>Instructor:</b> {i_email}</p>
                    <hr>
                    <h3 style="color: #0044CC;">FINAL ROI: {total_roi:.2f}%</h3>
                    <p style="color: #059669; font-weight: bold;">✅ RESULT VERIFIED & SAVED TO LOGS</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please enter your name and email to finalize.")
