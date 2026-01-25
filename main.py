import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

# --- 1. التصميم الرسمي الأبيض (نفس الصور المرفقة) ---
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
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800; }
    .stButton>button { 
        background-color: #FFFFFF; color: #111827; border: 1px solid #D1D5DB; 
        border-radius: 6px; font-weight: bold; padding: 0.5em 2em;
    }
    .stButton>button:hover { border-color: #0044CC; color: #0044CC; }
    .report-card { 
        background-color: #F9FAFB; border: 2px solid #E5E7EB; border-radius: 12px; 
        padding: 30px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والجلسة ---
def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 1, 'balance': 1000000.0, 'history': [1000000.0],
        'portfolio': {"Equities": 0, "Fixed Income": 0, "Commodities": 0},
        'prices': {"Equities": 500.0, "Fixed Income": 100.0, "Commodities": 200.0},
        'event': "Welcome, Trader. Configure your strategy to begin."
    })

with st.sidebar:
    st.header("⚙️ Control Panel")
    if st.button("🔄 Restart Simulation"):
        reset_game()

def process_turn():
    scenarios = [
        {"msg": "🚀 Market News: Tech sector rally!", "e": 0.08, "f": -0.01, "c": -0.02},
        {"msg": "⚠️ Volatility Alert: Gold is rising.", "e": -0.05, "f": 0.02, "c": 0.10},
        {"msg": "🏦 Central Bank Update: Interest rates stable.", "e": 0.01, "f": 0.01, "c": -0.01}
    ]
    sel = np.random.choice(scenarios)
    st.session_state.event = sel["msg"]
    # تحديث الأسعار (تم توحيد المسميات لمنع KeyError)
    st.session_state.prices["Equities"] *= (1 + sel["e"])
    st.session_state.prices["Fixed Income"] *= (1 + sel["f"])
    st.session_state.prices["Commodities"] *= (1 + sel["c"])
    
    total_val = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
    st.session_state.history.append(total_val)
    st.session_state.step += 1

# --- 3. الواجهة الرئيسية (Round 1-5) ---
st.title("🏛️ Professional Investment Strategy Lab")

if st.session_state.step <= 5:
    st.info(f"Round: {st.session_state.step} of 5 | 📢 {st.session_state.event}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("AVAILABLE CASH", f"${st.session_state.balance:,.0f}")
    c2.metric("PORTFOLIO VALUE (AUM)", f"${st.session_state.history[-1]:,.2f}")
    roi = ((st.session_state.history[-1] - 1000000)/1000000)*100
    c3.metric("CURRENT ROI", f"{roi:.2f}%")

    with st.form("trade_form"):
        st.write("### 🛠️ Portfolio Allocation")
        col_a, col_b, col_c = st.columns(3)
        s = col_a.slider("Equities %", 0, 100, 40)
        b = col_b.slider("Fixed Income %", 0, 100, 30)
        g = col_c.slider("Commodities %", 0, 100, 30)
        
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

# --- 4. شاشة النتائج النهائية وإصدار التقارير ---
else:
    st.success("🎯 Simulation Completed Successfully!")
    final_aum = st.session_state.history[-1]
    total_roi = ((final_aum - 1000000)/1000000)*100
    
    # الرسم البياني (تم حل NameError)
    fig = go.Figure(go.Scatter(y=st.session_state.history, mode='lines+markers', line=dict(color='#0044CC', width=3), fill='tozeroy'))
    fig.update_layout(title="Performance History", plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📝 Student Assessment & Submission")
    name = st.text_input("Enter Student Full Name:")
    instructor = st.text_input("Enter Instructor Email:")

    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        if st.button("🔄 Try Again to Improve ROI", use_container_width=True):
            reset_game()

    with res_col2:
        if name and instructor:
            # توليد ملف Excel
            df_report = pd.DataFrame({
                "Student Name": [name], "Instructor": [instructor],
                "Final Portfolio": [f"${final_aum:,.2f}"], "Total ROI": [f"{total_roi:.2f}%"]
            })
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_report.to_excel(writer, index=False, sheet_name='Result')
            
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name=f"Report_{name}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
