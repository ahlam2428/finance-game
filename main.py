import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="محاكي الاستثمار الاستراتيجي", layout="wide")

# تخصيص التصميم
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# تهيئة بيانات الجلسة (Session State)
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.balance = 1000000.0
    st.session_state.portfolio = {"الأسهم": 0, "السندات": 0, "الذهب": 0}
    st.session_state.history = []
    st.session_state.prices = {"الأسهم": 200.0, "السندات": 100.0, "الذهب": 1800.0}
    st.session_state.event = "بداية اللعبة: وزع محفظتك بحكمة."

# دالة لتحديث السوق بناءً على أحداث عشوائية
def next_turn(allocations):
    events = [
        {"msg": "رفع سعر الفائدة من البنك المركزي!", "stock": -0.10, "bond": -0.05, "gold": -0.02},
        {"msg": "طفرة تقنية ونمو اقتصادي غير متوقع.", "stock": 0.15, "bond": 0.02, "gold": -0.05},
        {"msg": "توترات جيوسياسية ترفع الطلب على الملاذات الآمنة.", "stock": -0.12, "bond": 0.05, "gold": 0.10},
        {"msg": "انخفاض معدلات التضخم عالمياً.", "stock": 0.08, "bond": 0.10, "gold": -0.08}
    ]
    
    selected_event = np.random.choice(events)
    st.session_state.event = selected_event["msg"]
    
    # تحديث الأسعار
    for asset in st.session_state.prices:
        change = selected_event.get(asset.lower(), np.random.uniform(-0.02, 0.02))
        st.session_state.prices[asset] *= (1 + change)
    
    # حساب القيمة الإجمالية للمحفظة
    total_value = st.session_state.balance
    for asset, qty in st.session_state.portfolio.items():
        total_value += qty * st.session_state.prices[asset]
    
    st.session_state.history.append(total_value)
    st.session_state.step += 1

# واجهة المستخدم
st.title("📊 محاكي الاستثمار الاستراتيجي (الدراسات العليا)")
st.info(f"📅 الجولة: {st.session_state.step} | 📢 الحدث الحالي: {st.session_state.event}")

col1, col2, col3 = st.columns(3)
col1.metric("السيولة النقدية", f"{st.session_state.balance:,.2f} ر.س")
col2.metric("إجمالي قيمة المحفظة", f"{st.session_state.history[-1] if st.session_state.history else 1000000:,.2f} ر.س")
col3.metric("عدد الأصول المملوكة", sum(st.session_state.portfolio.values()))

if st.session_state.step <= 5:
    st.subheader("🛠 إدارة المحفظة")
    with st.form("trade_form"):
        c1, c2, c3 = st.columns(3)
        s_pct = c1.slider("الأسهم (%)", 0, 100, 0)
        b_pct = c2.slider("السندات (%)", 0, 100, 0)
        g_pct = c3.slider("الذهب (%)", 0, 100, 0)
        
        submitted = st.form_submit_button("تأفيذ التوزيع والانتقال للجولة التالية")
        
        if submitted:
            if s_pct + b_pct + g_pct > 100:
                st.error("خطأ: إجمالي التوزيع يتجاوز 100%!")
            else:
                # بيع الأصول القديمة والتحول للتوزيع الجديد
                total_cash = st.session_state.balance + sum(q * st.session_state.prices[a] for a, q in st.session_state.portfolio.items())
                st.session_state.portfolio["الأسهم"] = (total_cash * (s_pct/100)) / st.session_state.prices["الأسهم"]
                st.session_state.portfolio["السندات"] = (total_cash * (b_pct/100)) / st.session_state.prices["السندات"]
                st.session_state.portfolio["الذهب"] = (total_cash * (g_pct/100)) / st.session_state.prices["الذهب"]
                st.session_state.balance = total_cash * (1 - (s_pct+b_pct+g_pct)/100)
                next_turn(None)
                st.rerun()

else:
    st.success("✅ انتهت اللعبة! إليك تقرير الأداء النهائي للمدرب:")
    
    final_value = st.session_state.history[-1]
    return_pct = ((final_value - 1000000) / 1000000) * 100
    
    # حساب نسبة شارب تقريبية (MIS Metric)
    volatility = np.std(st.session_state.history) if len(st.session_state.history) > 1 else 1
    sharpe = (return_pct / (volatility/10000)) if volatility != 0 else 0

    res_c1, res_c2, res_c3 = st.columns(3)
    res_c1.metric("العائد النهائي", f"{return_pct:.2f}%")
    res_c2.metric("مستوى المخاطرة (Volatility)", f"{volatility:,.0f}")
    res_c3.metric("كفاءة المحفظة (Sharpe Ratio)", f"{sharpe:.2f}")

    # رسم بياني للأداء
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.history, mode='lines+markers', name='قيمة المحفظة'))
    fig.update_layout(title="منحنى أداء المستثمر عبر الجولات", xaxis_title="الجولة", yaxis_title="القيمة")
    st.plotly_chart(fig)

    # تصدير البيانات للمدرب
    df_results = pd.DataFrame({
        "المعيار": ["صافي الربح", "العائد %", "تقييم المخاطر", "نسبة شارب"],
        "القيمة": [final_value, f"{return_pct:.2f}%", volatility, sharpe]
    })
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_results.to_excel(writer, index=False, sheet_name='النتائج')
    st.download_button("تحميل تقرير التفوق للمدرب (Excel)", data=output.getvalue(), file_name="investment_results.xlsx")

    if st.button("إعادة اللعب"):
        st.session_state.clear()
        st.rerun()
