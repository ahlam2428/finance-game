import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. إعدادات الواجهة البيضاء الاحترافية ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    /* تنسيق المربعات الكبيرة للنتائج مثل الصورة */
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; 
        border: 1px solid #D1D5DB; 
        border-radius: 10px; 
        padding: 30px; 
        margin-bottom: 10px;
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.8rem !important; }
    [data-testid="stMetricLabel"] { font-size: 1rem !important; text-transform: uppercase; color: #4B5563; }
    
    /* تنسيق الحاوية الجانبية لإدخال البيانات */
    .submission-box { 
        background-color: #F3F4F6; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الجلسة والبيانات ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'event': "Welcome. Round 1 is active."
    })

def reset_game():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

def process_turn():
    scenarios = [{"msg": "Market Growth", "e": 0.05, "f": 0.01, "c": -0.01}, {"msg": "Market Drop", "e": -0.04, "f": 0.02, "c": 0.05}]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(val)
    st.session_state.step += 1

# --- 3. عرض اللعب (حتى الجولة 5) ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"Round: {st.session_state.step} of 5 | 📢 {st.session_state.event}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("Current ROI", f"{roi:.2f}%")

    with st.form("trade"):
        st.write("### Portfolio Allocation")
        col_a, col_b, col_c = st.columns(3)
        s = col_a.slider("Equities %", 0, 100, 40)
        b = col_b.slider("Fixed Income %", 0, 100, 30)
        g = col_c.slider("Commodities %", 0, 100, 30)
        if st.form_submit_button("EXECUTE TRADES"):
            if s+b+g <= 100:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v*(s/100))/st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v*(b/100))/st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v*(g/100))/st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (s+b+g)/100)
                process_turn()
                st.rerun()
            else: st.error("Total exceeds 100%")

# --- 4. شاشة النتائج النهائية (نفس تصميم صورتك image_fb7674.png) ---
else:
    st.success("🎯 Simulation Completed! Your final report is ready.")
    final_val = st.session_state.history[-1]
    total_roi = ((final_val - 1000000)/1000000)*100

    # الرسم البياني في الأعلى
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC', width=3), fill='tozeroy'))
    fig.update_layout(title="Portfolio Value History", height=300, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # تقسيم الصفحة لنتائج وتسجيل (مثل الصورة)
    col_results, col_submit = st.columns([1.5, 1])

    with col_results:
        st.write("### 📊 Final Assessment")
        st.metric("FINAL VALUE", f"${final_val:,.2f}")
        st.metric("TOTAL ROI", f"{total_roi:.2f}%")
        if st.button("🔄 Restart & Try Again"): reset_game()

    with col_submit:
        st.write("### 📝 Official Submission")
        u_name = st.text_input("Enter Your Full Name:")
        i_name = st.text_input("Instructor Name:")
        
        if u_name and i_name:
            # تجهيز ملف الإكسل للتحميل
            df = pd.DataFrame({"Student": [u_name], "Instructor": [i_name], "ROI": [f"{total_roi:.2f}%"], "Final Value": [f"${final_val:,.2f}"]})
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
            st.info("After downloading, you can submit this file to your instructor.")
