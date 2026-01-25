import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. التنسيق الاحترافي (نفس صورك تماماً) ---
st.set_page_config(page_title="Strategic Investment Lab", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* مربعات النتائج الكبيرة */
    div[data-testid="stMetric"] { 
        background-color: #F8F9FA; border: 1px solid #D1D5DB; 
        border-radius: 12px; padding: 25px; margin-bottom: 15px;
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; font-size: 2.5rem !important; }
    h1, h2, h3 { color: #111827 !important; font-family: 'Arial'; }
    
    /* تنسيق أزرار الأكشن */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'event': "📢 System Ready. Configure Round 1."
    })

def reset_simulation():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

def next_round():
    scenarios = [{"m": "Market Up", "e": 0.06, "f": -0.01, "c": -0.02}, {"m": "Market Down", "e": -0.05, "f": 0.02, "c": 0.08}]
    s = np.random.choice(scenarios)
    st.session_state.event = s["m"]
    st.session_state.prices["Equities"] *= (1 + s["e"])
    st.session_state.prices["Fixed Income"] *= (1 + s["f"])
    st.session_state.prices["Commodities"] *= (1 + s["c"])
    val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(val)
    st.session_state.step += 1

# --- 3. محاكاة الجولات ---
st.title("🏛️ Strategic Investment & Portfolio Lab")

if st.session_state.step <= 5:
    st.info(f"Round {st.session_state.step} of 5 | {st.session_state.event}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Available Cash", f"${st.session_state.balance:,.0f}")
    c2.metric("Portfolio Value", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("Current ROI", f"{roi:.2f}%")

    with st.form("trade_input"):
        st.write("### Portfolio Allocation (%)")
        cols = st.columns(3)
        eq = cols[0].slider("Equities", 0, 100, 40)
        fi = cols[1].slider("Fixed Income", 0, 100, 30)
        co = cols[2].slider("Commodities", 0, 100, 30)
        if st.form_submit_button("EXECUTE TRADES"):
            if eq+fi+co <= 100:
                v = st.session_state.history[-1]
                st.session_state.portfolio["Equities"] = (v*(eq/100))/st.session_state.prices["Equities"]
                st.session_state.portfolio["Fixed Income"] = (v*(fi/100))/st.session_state.prices["Fixed Income"]
                st.session_state.portfolio["Commodities"] = (v*(co/100))/st.session_state.prices["Commodities"]
                st.session_state.balance = v * (1 - (eq+fi+co)/100)
                next_round()
                st.rerun()
            else: st.error("Total allocation cannot exceed 100%")

# --- 4. شاشة النتائج النهائية (نفس صورة image_a6e6b3.png) ---
else:
    st.success("🎯 Simulation Completed! Review and submit your results.")
    final_val = st.session_state.history[-1]
    final_roi = ((final_val - 1000000)/1000000)*100

    # الرسم البياني
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC', width=3), fill='tozeroy'))
    fig.update_layout(title="Performance Curve", height=300, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    col_res, col_sub = st.columns([1.5, 1])

    with col_res:
        st.write("### 📊 Final Assessment")
        st.metric("FINAL VALUE", f"${final_val:,.2f}")
        st.metric("TOTAL ROI", f"{final_roi:.2f}%")
        if st.button("🔄 Restart & Try Again"): reset_simulation()

    with col_sub:
        st.write("### 📨 Official Submission")
        u_name = st.text_input("Enter Your Full Name:")
        i_email = st.text_input("Instructor Email:")

        if u_name and i_email:
            # 1. زر إرسال الإيميل (باستخدام HTML Form لتجنب Submission failed)
            email_body = f"Student: {u_name}, Final ROI: {final_roi:.2f}%, Final Value: ${final_val:,.2f}"
            form_html = f"""
                <form action="https://formsubmit.co/{i_email}" method="POST" target="_blank">
                    <input type="hidden" name="Student Name" value="{u_name}">
                    <input type="hidden" name="Final ROI" value="{final_roi:.2f}%">
                    <input type="hidden" name="Final Value" value="${final_val:,.2f}">
                    <input type="hidden" name="_subject" value="Investment Lab Result: {u_name}">
                    <button type="submit" style="width:100%; background-color:#00D1FF; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">
                        📧 Send Results to Instructor Email
                    </button>
                </form>
            """
            st.markdown(form_html, unsafe_allow_html=True)
            
            st.write("---")
            
            # 2. زر تحميل الإكسل (كوسيلة دعم إضافية)
            df = pd.DataFrame({"Student": [u_name], "ROI": [f"{final_roi:.2f}%"], "Value": [f"${final_val:,.2f}"]})
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
            st.download_button("📥 Download Excel Report", buf.getvalue(), f"Result_{u_name}.xlsx", "application/vnd.ms-excel")
