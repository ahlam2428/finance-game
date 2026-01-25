import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. التنسيق الاحترافي ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; border: 1px solid #D1D5DB; 
        border-radius: 12px; padding: 25px; margin-bottom: 15px;
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.5rem !important; }
    
    /* تنسيق زر الإرسال السماوي */
    .send-btn {
        background-color: #00D1FF !important;
        color: white !important;
        border: none !important;
        padding: 15px !important;
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        display: block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'event': "System Ready."
    })

def reset_simulation():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 3. محاكاة الجولات ---
if st.session_state.step <= 5:
    st.title("🏛️ Strategic Investment Lab")
    st.info(f"Round {st.session_state.step} of 5")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("ROI", f"{roi:.2f}%")

    with st.form("trade"):
        cols = st.columns(3)
        eq = cols[0].slider("Equities %", 0, 100, 40)
        fi = cols[1].slider("Fixed Income %", 0, 100, 30)
        co = cols[2].slider("Commodities %", 0, 100, 30)
        if st.form_submit_button("EXECUTE"):
            if eq+fi+co <= 100:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v*(eq/100))/st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v*(fi/100))/st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v*(co/100))/st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (eq+fi+co)/100)
                # Next round logic
                st.session_state.prices["Equities"] *= (1 + np.random.uniform(-0.05, 0.07))
                st.session_state.prices["Fixed Income"] *= (1 + np.random.uniform(-0.01, 0.02))
                st.session_state.prices["Commodities"] *= (1 + np.random.uniform(-0.03, 0.05))
                st.session_state.history.append(st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items()))
                st.session_state.step += 1
                st.rerun()
            else: st.error("Exceeds 100%")

# --- 4. شاشة النتائج النهائية مع الزر المطلوب ---
else:
    st.title("🎯 Final Assessment Report")
    final_val = st.session_state.history[-1]
    final_roi = ((final_val - 1000000)/1000000)*100

    col_res, col_sub = st.columns([1.5, 1])

    with col_res:
        st.metric("FINAL VALUE", f"${final_val:,.2f}")
        st.metric("TOTAL ROI", f"{final_roi:.2f}%")
        fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC')))
        st.plotly_chart(fig, use_container_width=True)
        if st.button("🔄 Restart & Improve Performance"): reset_simulation()

    with col_sub:
        st.write("### 📨 Submit Results")
        student_name = st.text_input("Enter Your Full Name:")
        instructor_email = st.text_input("Enter Instructor Email:")

        if student_name and instructor_email:
            # زر إرسال الإيميل (HTML Form)
            # هذا هو الزر السماوي الذي سيتعامل مع الإيميل المكتوب في الخانة أعلاه
            email_form = f"""
                <form action="https://formsubmit.co/{instructor_email}" method="POST">
                    <input type="hidden" name="Student Name" value="{student_name}">
                    <input type="hidden" name="Final ROI" value="{final_roi:.2f}%">
                    <input type="hidden" name="Total Value" value="${final_val:,.2f}">
                    <input type="hidden" name="_next" value="https://strategic-lab.streamlit.app/">
                    <button type="submit" class="send-btn">
                        📧 Send Results to Instructor
                    </button>
                </form>
            """
            st.markdown(email_form, unsafe_allow_html=True)
            
            st.write("---")
            # زر تحميل الإكسل كنسخة احتياطية
            df = pd.DataFrame({"Student": [student_name], "ROI": [f"{final_roi:.2f}%"]})
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Excel Copy", buf.getvalue(), "Result.xlsx")
        else:
            st.warning("Please fill in your name and instructor's email to enable submission.")
