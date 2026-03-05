import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة الإبداعي (Purple Neon & Dark Luxury)
st.markdown("""
    <style>
    /* الخلفية العامة باللون الأسود العميق */
    .stApp {
        background-color: #080808;
        color: #f0f0f0;
    }
    /* تصميم البطاقات الزجاجية بتوهج بنفسجي */
    .metric-card {
        background: rgba(123, 31, 162, 0.05);
        border: 1px solid rgba(186, 104, 200, 0.2);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: 0.4s ease-in-out;
    }
    .metric-card:hover {
        border-color: #ba68c8;
        box-shadow: 0 0 25px rgba(186, 104, 200, 0.2);
        transform: translateY(-5px);
    }
    /* العناوين البنفسجية المتوهجة */
    h1 {
        color: #e1bee7;
        text-shadow: 0 0 20px rgba(171, 71, 188, 0.6);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 3px;
        text-align: center;
        text-transform: uppercase;
    }
    .status-gold {
        background: linear-gradient(45deg, #9c27b0, #e1bee7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 2em;
    }
    /* تعديل الأزرار للون البنفسجي المتدرج */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, #7b1fa2, #9c27b0);
        color: white;
        font-weight: bold;
        border: none;
        padding: 15px;
        font-size: 1.1em;
        box-shadow: 0 5px 20px rgba(123, 31, 162, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #9c27b0, #ba68c8);
        box-shadow: 0 8px 25px rgba(156, 39, 176, 0.6);
    }
    /* تخصيص شريط البحث */
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #4a148c;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. الهيدر والشعار
st.markdown("<h1>📡 CASH RADAR PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa; font-size: 1.1em;'>نظام التقصي المالي المتطور | النخبة الاستثمارية</p>", unsafe_allow_html=True)

# الجانب الأيسر (التحكم)
with st.sidebar:
    st.markdown("<h3 style='color: #ba68c8;'>📊 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح البنفسجي ⚡")
    st.write("---")
    st.markdown("<small style='color: #888;'>تحليل ذكي يعتمد على خوارزميات بافيت وجراهام مع تدقيق تشغيلي فائق.</small>", unsafe_allow_html=True)

# المحرك المالي الشامل
if scan_btn:
    with st.spinner("جاري اختراق القوائم المالية وتحليل البيانات..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        financials = stock.financials
        divs = stock.dividends
        
        if not financials.empty and 'regularMarketPrice' in info:
            score = 0
            results = []
            sector = info.get('sector', 'Default')
            price = info.get('regularMarketPrice', 1)

            # --- محرك التحليل (المعايير الـ 10) ---
            # (نفس المعايير الدقيقة السابقة)
            y_divs = divs.groupby(divs.index.year).sum()
            div_yrs = len(y_divs)
            if div_yrs >= 10: score += 1; results.append(f"✅ استمرارية التوزيع: {div_yrs} سنة")
            else: results.append(f"❌ سجل توزيع قصير: {div_yrs} سنة")

            if div_yrs >= 5:
                growth = (y_divs.iloc[-1] / y_divs.iloc[-5]) - 1 if y_divs.iloc[-5] != 0 else 0
                if growth > 0: score += 1; results.append(f"✅ نمو التوزيعات: +{growth*100:.1f}%")
                else: results.append("❌ لا يوجد نمو مستدام")

            incomes = financials.loc['Net Income'].tail(10) if 'Net Income' in financials.index else []
            if (pd.Series(incomes) > 0).sum() >= 9: score += 1; results.append("✅ سجل أرباح نظيف (9/10 سنوات)")
            else: results.append("❌ أرباح متذبذبة")

            op_inc = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else 0
            shares = info.get('sharesOutstanding', 1)
            pe_op = price / (op_inc / shares) if op_inc > 0 else 99
            if 0 < pe_op <= 20: score += 1; results.append(f"✅ مكرر تشغيلي عادل: {pe_op:.2f}")
            else: results.append(f"❌ مكرر تشغيلي مرتفع: {pe_op:.2f}")

            payout = info.get('payoutRatio', 0)
            if 0.2 <= payout <= 0.7: score += 1; results.append(f"✅ نسبة توزيع متزنة: {payout*100:.1f}%")
            else: results.append(f"❌ نسبة توزيع غير آمنة: {payout*100:.1f}%")

            cr = info.get('currentRatio', 0)
            if cr >= 1.5: score += 1; results.append(f"✅ سيولة قوية: {cr:.2f}")
            else: results.append(f"❌ سيولة ضعيفة: {cr:.2f}")

            de = info.get('debtToEquity', 0) / 100
            limit = 0.8 if sector in ['Utilities', 'Energy', 'Real Estate'] else 0.5
            if de <= limit: score += 1; results.append(f"✅ ديون آمنة للقطاع: {de:.2f}")
            else: results.append(f"❌ ديون مرتفعة: {de:.2f}")

            roe = info.get('returnOnEquity', 0)
            if roe >= 0.15: score += 1; results.append(f"✅ كفاءة الإدارة (ROE): {roe*100:.1f}%")
            else: results.append(f"❌ عائد حقوق مساهمين ضعيف: {roe*100:.1f}%")

            net_inc = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else 1
            if net_inc <= (op_inc * 1.25): score += 1; results.append("✅ جودة أرباح عالية (تشغيلية)")
            else: results.append("❌ أرباح ناتجة عن بنود عرضية")

            eg = info.get('earningsQuarterlyGrowth', 0)
            if eg >= 0.05: score += 1; results.append(f"✅ نمو أرباح السهم: +{eg*100:.1f}%")
            else: results.append("❌ نمو أرباح ضعيف")

            # --- العرض الإبداعي للنتائج ---
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.markdown(f"<div class='metric-card'><h5>السعر الحالي</h5><h3 style='color:#e1bee7;'>{price}</h3></div>", unsafe_allow_html=True)
            with col2: st.markdown(f"<div class='metric-card'><h5>المكرر التشغيلي</h5><h3 style='color:#e1bee7;'>{pe_op:.1f}</h3></div>", unsafe_allow_html=True)
            with col3: st.markdown(f"<div class='metric-card'><h5>عائد التوزيع</h5><h3 style='color:#e1bee7;'>{info.get('dividendYield',0)*100:.1f}%</h3></div>", unsafe_allow_html=True)
            with col4: st.markdown(f"<div class='metric-card'><h5>الملاءة المالية</h5><h3 style='color:#e1bee7;'>{de:.2f}</h3></div>", unsafe_allow_html=True)

            st.write("---")
            
            # عرض الحالة النهائية بتصميم متوهج
            if score >= 8:
                st.markdown(f"<div style='text-align:center;'><span class='status-gold'>🏆 التصنيف: سهم أرستقراطي ذهبي ({score}/10)</span></div>", unsafe_allow_html=True)
                st.balloons()
            elif score >= 5:
                st.markdown(f"<div style='text-align:center;'><span style='color:#ba68c8; font-size:1.5em;'>🟡 التصنيف: سهم عوائد جيد ({score}/10)</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center;'><span style='color:#e74c3c; font-size:1.5em;'>🔴 التصنيف: فخ عائد - مخاطرة عالية ({score}/10)</span></div>", unsafe_allow_html=True)

            # تفاصيل الرادار في قائمة منسدلة أنيقة
            with st.expander("👁️ عرض التقرير التفصيلي لعملية المسح"):
                for r in results:
                    st.write(r)
        else:
            st.error("❌ فشل الاتصال: تعذر العثور على بيانات السهم المطلوبة.")

st.markdown("<br><p style='text-align: center; color: #444; font-size: 0.8em;'>تم التطوير لدعم اتخاذ القرار الاستثماري المبني على الأرقام الحقيقية</p>", unsafe_allow_html=True)
