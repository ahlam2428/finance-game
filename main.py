import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. إعدادات الواجهة البيضاء ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; border: 1px solid #D1D5DB; 
        border-radius: 12px; padding: 25px; margin-bottom: 15px;
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.5rem !important; }
    
    /* تنسيق زر الإرسال السماوي (مثل الصورة المرفقة) */
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
        display: block;
        margin-top: 10px;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الجلسة ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0}
    })

def reset_game():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 3. جولات اللعب ---
if st.session_state.step <= 5:
    st.title("🏛️ Strategic Investment Lab")
    st.info(f"Round {st.session_state.step} of 5")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("Current ROI", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.write("### Allocation")
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
                
                # تحديث الأسعار للجولة القادمة
                st.session_state.prices["Equities"] *= (1 + np.random.uniform(-0.04, 0.06))
                st.session_state.prices["Fixed Income"] *= (1 + np.random.uniform(-0.01, 0.02))
                st.session_state.prices["Commodities"] *= (1 + np.random.uniform(-0.02, 0.04))
                
                new_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
                st.session_state.history.append(new_val)
                st.session_state.step += 1
                st.rerun()
            else: st.error("Total exceeds 100%")

# --- 4. شاشة النتائج النهائية (حل مشاكل الـ KeyError والـ NameError) ---
else:
    st.title("🎯 Final Assessment")
    final_val = st.session_state.history[-1]
    final_roi = ((final_val - 1000000)/1000000)*100

    col_res, col_sub = st.columns([1.5, 1])

    with col_res:
        st.metric("FINAL VALUE", f"${final_val:,.2f}")
        st.metric("TOTAL ROI", f"{final_roi:.2f}%")
        # رسم بياني بسيط لتجنب NameError
        fig_final = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC')))
        st.plotly_chart(fig_final, use_container_width=True)
        if st.button("🔄 Restart & Try Again"): reset_game()

    with col_sub:
        st.write("### 📨 Official Submission")
        u_name = st.text_input("Student Full Name:")
        i_email = st.text_input("Instructor Email:")

        if u_name and i_email:
            # زر الإرسال السماوي المفقود
            email_body = f"Results for {u_name}: ROI {final_roi:.2f}%"
            form_html = f"""
                <form action="https://formsubmit.co/{i_email}" method="POST">
                    <input type="hidden" name="Student Name" value="{u_name}">
                    <input type="hidden" name="Final ROI" value="{final_roi:.2f}%">
                    <input type="hidden" name="Total Value" value="${final_val:,.2f}">
                    <input type="hidden" name="_subject" value="Investment Lab Result - {u_name}">
                    <button type="submit" class="send-btn">
                        📧 Send Results to Instructor Email
                    </button>
                </form>
            """
            st.markdown(form_html, unsafe_allow_html=True)
            
            st.write("---")
            # زر تحميل CSV (بديل للإكسل لتجنب ModuleNotFoundError في الصورة 12)
            csv = pd.DataFrame({"Student": [u_name], "ROI": [final_roi]}).to_csv(index=False)
            st.download_button("📥 Download Results (CSV)", csv, f"Result_{u_name}.csv", "text/csv")
        else:
            st.warning("Enter name and email to enable submission.")
