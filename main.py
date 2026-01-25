import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# --- 1. التصميم الرسمي الأبيض ---
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
    
    /* تنسيق زر الإعادة الأحمر */
    .reset-btn { color: #DC2626 !important; border-color: #DC2626 !important; }
    
    .stButton>button { 
        border-radius: 6px; font-weight: bold; padding: 0.5em 2em;
    }
    .report-card { 
        background-color: #F9FAFB; border: 2px solid #0044CC; border-radius: 12px; 
        padding: 30px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة تصفير البيانات (Reset Function) ---
def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. إدارة الجلسة والبيانات ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 490.0, "Fixed Income": 92.0, "Commodities": 180.0},
        'event': "📢 System Ready. Configure your first allocation."
    })

# إضافة زر إعادة في الشريط الجانبي متاح دائماً
with st.sidebar:
    st.header("⚙️ Lab Settings")
    if st.button("🔄 Reset & Restart Simulation", use_container_width=True):
        reset_game()
    st.markdown("---")
    st.caption("Student: Use this to restart if you want to improve your performance.")

def process_turn():
    scenarios = [
        {"msg": "🚀 Market Growth: Equities Outperform!", "e": 0.09, "f": -0.01, "c": -0.03},
        {"msg": "⚠️ Inflation Spike: Commodities are Rising.", "e": -0.06, "f": 0.02, "c": 0.12},
        {"msg": "🏦 Neutral Policy: Market Stability.", "e": 0.02, "f": 0.01, "c": -0.01}
    ]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. واجهة اللعب ---
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
        s = col_a.slider("Equities (Stocks) %", 0, 100, 40)
        b = col_b.slider("Fixed Income (Bonds) %", 0, 100, 30)
        g = col_c.slider("Commodities (Gold) %", 0, 100, 30)
        if st.form_submit_button("EXECUTE TRADES"):
            if s + b + g > 100:
                st.error("Error: Allocation exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. شاشة النتائج النهائية ---
else:
    st.success("🎯 Simulation Completed!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC', width=3)))
    fig.update_layout(title="Portfolio Value Performance Chart", plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write("### 📊 Performance Summary")
        st.metric("Final ROI", f"{total_roi:.2f}%")
        # زر الإعادة في شاشة النتائج
        if st.button("🔄 Try Again to Improve ROI", type="primary"):
            reset_game()

    with col_res2:
        st.write("### 🎓 Final Submission")
        name = st.text_input("Student Name:")
        email = st.text_input("Instructor Email:")
        if st.button("Submit Official Report"):
            if name and email:
                st.balloons()
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #0044CC;">OFFICIAL PERFORMANCE REPORT</h2>
                    <p><b>Student:</b> {name} | <b>Instructor:</b> {email}</p>
                    <hr>
                    <h3 style="color: #059669;">Final ROI: {total_roi:.2f}%</h3>
                    <p style="font-weight: bold;">Verified Strategy Output</p>
                </div>
                """, unsafe_allow_html=True)
