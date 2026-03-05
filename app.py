import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="كاش رادار | نسخة النخبة الاستثمارية", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00c853;'>📡 كاش رادار: التدقيق المالي المعتمد</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>تحليل شامل وفق معايير (بنجامين جراهام، وارن بافيت، وبيتر لينش)</p>", unsafe_allow_html=True)

symbol = st.sidebar.text_input("🔍 رمز السهم (مثال: 2222):", "2222")

if st.sidebar.button("تشغيل المسح العميق 🚀"):
    with st.spinner("جاري فحص القوائم المالية وتطبيق معايير النخبة..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        divs = stock.dividends
        
        if not divs.empty and 'regularMarketPrice' in info:
            score = 0
            results = []

            # --- المحور الأول: سجل التاريخ (الماضي) ---
            yearly_divs = divs.groupby(divs.index.year).sum()
            div_years_count = len(yearly_divs)
            
            # 1. سجل التوزيعات
            if div_years_count >= 10:
                score += 1
                results.append(f"✅ **مؤشر استمرارية التوزيعات:** الشركة وزعت لـ ({div_years_count}) سنة مستمرة. (المعيار: > 10 سنوات)")
            else:
                results.append(f"❌ **مؤشر استمرارية التوزيعات:** السجل قصير ({div_years_count}) سنة فقط. (المعيار: > 10 سنوات)")

            # 2. نمو التوزيع (آخر 5 سنوات)
            if len(yearly_divs) >= 5:
                last_5 = yearly_divs.tail(5)
                growth = ((last_5.iloc[-1] - last_5.iloc[0]) / last_5.iloc[0]) * 100
                if growth > 0:
                    score += 1
                    results.append(f"✅ **مؤشر نمو التوزيعات:** زادت بنسبة ({growth:.1f}%) خلال آخر 5 سنوات. (المعيار: نمو إيجابي)")
                else:
                    results.append(f"❌ **مؤشر نمو التوزيعات:** لم يتحقق نمو ({growth:.1f}%). (المعيار: نمو إيجابي)")

            # --- المحور الثاني: الملاءة المالية (الحاضر) ---
            # 3. نسبة التوزيع
            payout = (info.get('payoutRatio', 0) or 0) * 100
            if 20 <= payout <= 70:
                score += 1
                results.append(f"✅ **مؤشر نسبة التوزيع (Payout Ratio):** النسبة مثالية ({payout:.1f}%). (المعيار: 20% - 70%)")
            else:
                results.append(f"❌ **مؤشر نسبة التوزيع (Payout Ratio):** النسبة غير متزنة ({payout:.1f}%). (المعيار: 20% - 70%)")

            # 4. نسبة السيولة
            curr_ratio = info.get('currentRatio', 0) or 0
            if curr_ratio >= 1.5:
                score += 1
                results.append(f"✅ **مؤشر نسبة السيولة (Current Ratio):** سيولة قوية ({curr_ratio:.2f}). (المعيار: > 1.5)")
            else:
                results.append(f"❌ **مؤشر نسبة السيولة (Current Ratio):** سيولة ضعيفة ({curr_ratio:.2f}). (المعيار: > 1.5)")

            # 5. نسبة الديون
            de_ratio = info.get('debtToEquity', 0) or 0
            if 0 < de_ratio <= 60:
                score += 1
                results.append(f"✅ **مؤشر نسبة الديون (D/E Ratio):** ديون آمنة ({de_ratio:.1f}%). (المعيار: < 60%)")
            else:
                results.append(f"❌ **مؤشر نسبة الديون (D/E Ratio):** ديون مقلقة ({de_ratio:.1f}%). (المعيار: < 60%)")

            # --- المحور الثالث: الجودة والسعر (المستقبل) ---
            # 6. مكرر الربحية
            pe = info.get('trailingPE', 0) or 0
            if 0 < pe <= 20:
                score += 1
                results.append(f"✅ **مكرر الربحية (P/E Ratio):** السعر عادل حالياً ({pe:.2f}). (المعيار: < 20)")
            else:
                results.append(f"❌ **مكرر الربحية (P/E Ratio):** السعر متضخم ({pe:.2f}). (المعيار: < 20)")

            # 7. العائد على حقوق المساهمين
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            if roe >= 15:
                score += 1
                results.append(f"✅ **مؤشر كفاءة الإدارة (ROE):** كفاءة عالية ({roe:.1f}%). (المعيار: > 15%)")
            else:
                results.append(f"❌ **مؤشر كفاءة الإدارة (ROE):** كفاءة ضعيفة ({roe:.1f}%). (المعيار: > 15%)")

            # --- التقييم النهائي ---
            st.header(f"تقرير التدقيق المالي لشركة: {info.get('longName', symbol)}")
            st.write("---")
            
            if score >= 6:
                st.success(f"🏆 النتيجة النهائية لـ كاش رادار: {score}/7 | السهم ضمن النخبة الأرستقراطية.")
            elif score >= 4:
                st.warning(f"🟡 النتيجة النهائية لـ كاش رادار: {score}/7 | سهم عوائد جيد ولكن يحتاج لمراقبة.")
            else:
                st.error(f"🔴 النتيجة النهائية لـ كاش رادار: {score}/7 | فخ عائد محتمل - مخاطرة عالية.")

            # عرض القائمة التفصيلية بربط المؤشر بالنتيجة والمعيار
            st.subheader("📋 تفاصيل نتائج رادار النخبة:")
            for r in results:
                st.write(r)
                
            # إضافة الرسم البياني للتوزيعات
            with st.expander("👁️ تدقيق سجل التوزيعات السنوية الفعلي"):
                st.bar_chart(yearly_divs)
                st.table(yearly_divs.sort_index(ascending=False))
        else:
            st.error("❌ تعذر جلب بيانات التوزيعات أو الميزانية. تأكد من الرمز (مثال: 2222 للسوق السعودي).")
