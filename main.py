import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. الإعدادات والواجهة الرسمية (نفس الصور السابقة) ---
st.set_page_config(page_title="Professional Investment Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    /* تنسيق المربعات العلوية */
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        border: 1px solid #D1D5DB; 
        border-radius: 10px; 
        padding: 20px; 
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.2rem !important; }
    
    /* تنسيق النصوص والأزرار */
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Arial'; font-weight: bold !important; }
    .stButton>button { 
        background-color: #FFFFFF; color: #111827; border: 1px solid #D1D5DB; 
        border-radius: 6px; font-weight: bold; padding: 0.5em 2em;
    }
    .stButton>button:hover { border-color: #0044CC; color: #0044CC; }
    
    /* تصميم شهادة النتائج */
    .result-certificate { 
        background-color: #F0F9FF; border: 2px solid #0044CC; border-radius: 15px; 
        padding: 30px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. وظائف التحكم (إعادة المحاولة) ---
def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. تهيئة البيانات والجلسة (إصلاح KeyError) ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'event': "📢 Welcome. Set your allocation to start Round 1."
    })

# زر إعادة المحاولة في الشريط الجانبي
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🔄 Restart Simulation"):
        reset_game()

def process_turn():
    scenarios = [
        {"msg": "🚀 Tech Boom: Equities are surging!", "e": 0.08, "f": -0.01, "c": -0.02},
        {"msg": "⚠️ Inflation Alert: Commodities prices up.", "e": -0.05, "f": 0.03, "c": 0.12},
        {"msg": "🏦 Neutral Policy: Market is stable.", "e": 0.01, "f": 0.01, "c": -0.01}
    ]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    # تحديث الأسعار بمسميات موحدة
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 4. العرض الرئيسي للمحاكاة ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    st.info(f"📅 Round: {st.session_state.step} of 5 | {st.session_state.event}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("AVAILABLE CASH", f"${st.session_state.balance:,.0f}")
    c2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("CURRENT ROI", f"{roi:.2f}%")

    with st.form("trades"):
        st.write("### 🛠️ Portfolio Allocation")
        col_a, col_b, col_c = st.columns(3)
        s = col_a.slider("Equities %", 0, 100, 40)
        b = col_b.slider("Fixed Income %", 0, 100, 30)
        g = col_c.slider("Commodities %", 0, 100, 30)
        
        if st.form_submit_button("EXECUTE TRADES"):
            if s + b + g > 100:
                st.error("Error: Total allocation exceeds 100%!")
            else:
                v = st.session_state.history[-1]
                # حساب الكميات بناءً على الأسعار الحالية
                st.session_state.portfolio["Equities"] = (v * (s/100)) / st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v * (b/100)) / st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v * (g/100)) / st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()

# --- 5. شاشة النتائج النهائية وحفظ الملفات ---
else:
    st.success("🎯 Simulation Completed!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني (إصلاح NameError)
    fig = go.Figure(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#0044CC', width=3),
        fill='tozeroy', 
        fillcolor='rgba(0, 68, 204, 0.1)'
    ))
    fig.update_layout(title="Portfolio Performance History", plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📜 Save & Submit Results")
    u_name = st.text_input("Enter Your Name:")
    i_name = st.text_input("Enter Instructor Name:")

    res_c1, res_c2, res_c3 = st.columns(3)
    
    with res_c1:
        if st.button("🔄 Try Again for Higher ROI", use_container_width=True):
            reset_game()

    with res_c2:
        if st.button("📋 View Official Certificate", use_container_width=True):
            st.session_state.view_cert = True

    with res_c3:
        if u_name and i_name:
            # ميزة تصدير إكسل
            df = pd.DataFrame({
                "Student": [u_name], "Instructor": [i_name],
                "Final Value": [f"${final_aum:,.2f}"], "Total ROI": [f"{total_roi:.2f}%"]
            })
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Excel Report",
                data=buffer.getvalue(),
                file_name=f"Result_{u_name}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

    if st.session_state.get('view_cert'):
        st.markdown(f"""
            <div class="result-certificate">
                <h2 style="color: #0044CC;">Performance Certificate</h2>
                <p>Student: <b>{u_name}</b> | Instructor: <b>{i_name}</b></p>
                <hr>
                <h3>Final Score (ROI): {total_roi:.2f}%</h3>
                <p>Status: Verified & Ready for Submission ✅</p>
            </div>
        """, unsafe_allow_html=True)
