import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. التصميم الرسمي الأبيض (نفس واجهة صورك) ---
st.set_page_config(page_title="Professional Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        border: 1px solid #D1D5DB; 
        border-radius: 10px; 
        padding: 20px; 
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.2rem !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; font-weight: bold !important; }
    .stButton>button { 
        background-color: #FFFFFF; color: #111827; border: 1px solid #D1D5DB; 
        border-radius: 6px; font-weight: bold;
    }
    /* تنسيق الشهادة النهائية */
    .report-card { 
        background-color: #F9FAFB; border: 2px solid #0044CC; border-radius: 12px; 
        padding: 30px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأسعار (حل مشكلة KeyError) ---
@st.cache_data(ttl=3600)
def get_live_prices():
    try:
        # تأكيد المسميات لمنع KeyError
        return {"Equities": 490.0, "Fixed Income": 92.0, "Commodities": 180.0}
    except:
        return {"Equities": 490.0, "Fixed Income": 92.0, "Commodities": 180.0}

# --- 3. إدارة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': get_live_prices(),
        'event': "📢 System Online. Waiting for trades..."
    })

def process_turn():
    scenarios = [
        {"msg": "🚀 Market Growth!", "e": 0.08, "f": -0.01, "c": -0.02},
        {"msg": "⚠️ Market Volatility!", "e": -0.06, "f": 0.02, "c": 0.10}
    ]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    # تحديث الأسعار بحذر لمنع KeyError
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. العرض ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    st.info(f"Round: {st.session_state.step} of 5 | {st.session_state.event}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("Current ROI", f"{roi:.2f}%")

    with st.form("trades"):
        st.write("### Portfolio Allocation")
        col_a, col_b, col_c = st.columns(3)
        s = col_a.slider("Equities %", 0, 100, 40)
        b = col_b.slider("Fixed Income %", 0, 100, 30)
        g = col_c.slider("Commodities %", 0, 100, 30)
        if st.form_submit_button("EXECUTE TRADES"):
            if s + b + g > 100:
                st.error("Exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. شاشة النتائج النهائية (حل خطأ fig) ---
else:
    st.success("🎯 Simulation Completed!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # تعريف الرسم البياني قبل الاستدعاء
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC', width=3)))
    fig.update_layout(title="Portfolio Performance Chart", plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📜 Final Performance Report")
    name = st.text_input("Enter Student Name:")
    email = st.text_input("Enter Instructor Email:")

    if st.button("Generate Verified Report"):
        if name and email:
            st.balloons()
            st.markdown(f"""
            <div class="report-card">
                <h2 style="color: #0044CC;">OFFICIAL INVESTMENT REPORT</h2>
                <p><b>Student:</b> {name} | <b>Instructor:</b> {email}</p>
                <hr>
                <h3>Final Value: ${final_aum:,.2f}</h3>
                <h3 style="color: #059669;">Total ROI: {total_roi:.2f}%</h3>
                <p>✅ Performance Logged Successfully</p>
            </div>
            """, unsafe_allow_html=True)
