import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Purple Neon & Dark Luxury)
st.markdown("""
    <style>
    .stApp { background-color: #080808; color: #f0f0f0; }
    .metric-card {
        background: rgba(123, 31, 162, 0.05);
        border: 1px solid rgba(186, 104, 200, 0.3);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        transition: 0.4s;
    }
    h1 { color: #e1bee7; text-shadow: 0 0 20px rgba(171, 71, 188, 0.6); text-align: center; font-family: 'Segoe UI'; }
    .status-text { font-size: 1.8em; font-weight: bold; text-align: center; margin: 20px 0; }
    .explanation { background: rgba(255,255,255,0.05); padding: 15px; border-right: 5px solid #9c27b0; margin-bottom: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>نظام التقصي المالي المتطور | نسخة التدقيق الشامل</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color: #ba68c8;'>📊 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (مثال: 2222):", "2222")
    scan_btn = st.button("تفعيل المسح البنفسجي ⚡")

if scan_btn:
    with st.spinner("جاري تنقية البيانات وحساب المؤشرات التشغيلية..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        financials = stock.financials
        divs = stock.dividends
        
        if not financials.empty and 'regularMarketPrice' in info:
            score = 0
            explanations = []
            price = info.get('regularMarketPrice', 1)
            sector = info.get('sector', 'Default')

            # --- محرك التحليل والتدقيق ---

            # 1. استمرارية التوزيعات
            y_divs = divs.groupby(divs.index.year).sum()
            div_yrs = len(y_divs)
            res = f"**مؤشر استمرارية التوزيع:** السهم وزع لـ ({div_yrs}) سنة."
            if div_yrs >= 10:
                score += 1
                explanations.append(f"✅ {res} (الشرح: تاريخ طويل يثبت قوة نموذج العمل)")
            else: explanations.append(f"❌ {res} (الشرح: السجل القصير يزيد من مخاطر عدم الاستدامة)")

            # 2. مكرر الربحية التشغيلي (استبعاد الأرباح العرضية)
            op_inc = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else 0
            pe_op = price / (op_inc / info.get('sharesOutstanding', 1)) if op_inc > 0 else 0
            res = f"**مؤشر المكرر التشغيلي:** القيمة ({pe_op:.2f})."
            if 0 < pe_op <= 20:
                score += 1
                explanations.append(f"✅ {res} (الشرح: السعر عادل مقارنة بالأرباح الناتجة عن النشاط الأساسي لا بيع الأصول)")
            else: explanations.append(f"❌ {res} (الشرح: السعر متضخم أو الأرباح التشغيلية ضعيفة)")

            # 3. نسبة التوزيع (Payout Ratio) - تصحيح الحساب
            payout = info.get('payoutRatio', 0)
            if payout > 1: payout = payout / 100 # تصحيح إذا جاءت كنسبة مئوية صحيحة
            res = f"**مؤشر نسبة التوزيع:** القيمة ({payout*100:.1f}%)."
            if 0.2 <= payout <= 0.7:
                score += 1
                explanations.append(f"✅ {res} (الشرح: الشركة توازن بين مكافأة المساهم وإعادة الاستثمار للنمو)")
            else: explanations.append(f"❌ {res} (الشرح: نسبة غير مستدامة؛ قد تضطر الشركة لخفض التوزيع مستقبلاً)")

            # 4. الملاءة المالية والديون (حسب القطاع)
            de = (info.get('debtToEquity', 0) or 0) / 100
            limit = 0.8 if sector in ['Utilities', 'Energy', 'Real Estate'] else 0.5
            res = f"**مؤشر نسبة الديون (D/E):** القيمة ({de:.2f})."
            if de <= limit:
                score += 1
                explanations.append(f"✅ {res} (الشرح: ديون آمنة ضمن حدود قطاع {sector})")
            else: explanations.append(f"❌ {res} (الشرح: ديون مرتفعة قد تلتهم الأرباح في حال رفع الفائدة)")

            # 5. كفاءة الإدارة (ROE)
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            res = f"**مؤشر كفاءة الإدارة (ROE):** القيمة ({roe:.1f}%)."
            if roe >= 15:
                score += 1
                explanations.append(f"✅ {res} (الشرح: الإدارة تستخدم حقوق المساهمين ببراعة لتوليد أرباح عالية)")
            else: explanations.append(f"❌ {res} (الشرح: العائد على الحقوق أقل من طموح مستثمري النخبة)")

            # --- عرض النتائج الفخمة ---
            st.write("### 💎 ملخص الرادار التشغيلي")
            c1, c2, c3 = st.columns(3)
            c1.metric("السعر الحالي", f"{price} ر.س")
            c2.metric("المكرر التشغيلي", f"{pe_op:.1f}")
            c3.metric("عائد التوزيع", f"{info.get('dividendYield',0)*100:.1f}%")

            st.write("---")
            if score >= 4:
                st.markdown(f"<div class='status-text' style='color:#ba68c8;'>🏆 التصنيف: سهم أرستقراطي ذهبي ({score}/5)</div>", unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"<div class='status-text' style='color:#e74c3c;'>⚠️ التصنيف: يحتاج تدقيق إضافي ({score}/5)</div>", unsafe_allow_html=True)

            st.write("### 📝 التقرير التفصيلي والشرح:")
            for exp in explanations:
                st.markdown(f"<div class='explanation'>{exp}</div>", unsafe_allow_html=True)

        else: st.error("❌ فشل المسح: تعذر الوصول للبيانات الحية.")
