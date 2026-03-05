import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO | Elite 2026", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Dark UI + Neon Accents)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; margin-bottom: 5px; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    
    /* تصميم الجدول المطور بالنيون */
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; }
    
    /* ذيل النيون للنتائج */
    .row-pass { border-bottom: 4px solid #03dac6 !important; box-shadow: 0 4px 10px rgba(3, 218, 198, 0.1); }
    .row-fail { border-bottom: 4px solid #cf6679 !important; box-shadow: 0 4px 10px rgba(207, 102, 121, 0.1); }
    
    .pass-text { color: #03dac6; font-weight: bold; }
    .fail-text { color: #cf6679; font-weight: bold; }
    .desc-text { color: #a0a0a0; font-size: 0.85em; line-height: 1.4; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")
st.markdown("<p style='text-align: center; color: #888;'>نظام التدقيق المالي المتكامل | بنجامين جراهام • وارن بافيت • بيتر لينش</p>", unsafe_allow_html=True)

# 3. مصفوفة ذكاء القطاعات
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 2.5, 'payout_avg': 55, 'roe_min': 15, 'note': "💡 قطاع مالي: السيولة تتبع معايير SAMA والديون ودائع."},
    'Technology': {'pe_limit': 25, 'de_limit': 0.4, 'payout_avg': 40, 'roe_min': 20, 'note': "🚀 تقنية: نركز على انعدام الديون وكفاءة الإدارة العالية."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'payout_avg': 90, 'roe_min': 8, 'note': "🏠 عقار: التوزيع المرتفع (90%+) هو معيار الأمان في الريتات."},
    'Utilities': {'pe_limit': 15, 'de_limit': 1.4, 'payout_avg': 65, 'roe_min': 10, 'note': "⚡ مرافق: استقرار التدفقات النقدية يسمح بمديونية أعلى قليلاً."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'payout_avg': 55, 'roe_min': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 لوحة التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 2222):", "2222")
    scan_btn = st.button("تفعيل المسح الراداري ✨")

if scan_btn:
    with st.spinner("جاري فحص 10 سنوات من القوائم المالية وتدقيق جودة الأرباح..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info, fin, divs, cf = stock.info, stock.financials, stock.dividends, stock.cashflow

            if 'regularMarketPrice' in info:
                price = info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                score = 0
                rows_html = ""

                # --- دالة إضافة البيانات المنظمة للجدول ---
                def add_to_table(name, result, criteria, philosophy, is_pass):
                    global score
                    if is_pass: score += 1
                    status_class = "row-pass" if is_pass else "row-fail"
                    text_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"""
                    <tr class='{status_class}'>
                        <td style='font-weight: bold;'>{name}</td>
                        <td class='{text_class}'>{icon} {result}</td>
                        <td>{criteria}</td>
                        <td class='desc-text'>{philosophy}</td>
                    </tr>
                    """

                # 1. المكرر التشغيلي (P/E)
                op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
                shares = info.get('sharesOutstanding', 1)
                pe_op = price / (op_inc / shares) if op_inc > 0 else 0
                rows_html += add_to_table("المكرر التشغيلي", f"{pe_op:.2f}", f"< {logic['pe_limit']}", "جراهام: نشتري الأرباح التشغيلية الحقيقية بسعر عادل لضمان هامش الأمان.", 0 < pe_op <= logic['pe_limit'])

                # 2. عائد التوزيع الحقيقي (يدوي)
                real_yield = (divs.last('365D').sum() / price) * 100 if not divs.empty else 0
                rows_html += add_to_table("عائد التوزيع", f"{real_yield:.2f}%", "> 4%", "لينش: العائد النقدي هو الدليل المادي الوحيد على صدق أرباح الشركة ومكافأة المستثمر.", real_yield >= 4.0)

                # 3. نسبة التوزيع (Payout)
                payout = (info.get('payoutRatio', 0) or 0) * 100
                if payout > 100: payout /= 100
                p_pass = 20 <= payout <= 75 if sector != 'Real Estate' else 70 <= payout <= 95
                rows_html += add_to_table("نسبة التوزيع (Payout)", f"{payout:.1f}%", "20% - 75%", "المعيار: النسبة المتزنة تحمي التوزيعات من القطع وتسمح للشركة بالنمو الذاتي.", p_pass)

                # 4. كفاءة الإدارة (ROE)
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                rows_html += add_to_table("كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"> {logic['roe_min']}%", "بافيت: قدرة الإدارة على توليد ثروة من كل ريال يملكه المساهمون.", roe >= logic['roe_min'])

                # 5. نسبة الديون (D/E)
                de = (info.get('debtToEquity', 0) or 0) / 100
                rows_html += add_to_table("نسبة الديون", f"{de:.2f}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة البنكية.", de <= logic['de_limit'])

                # 6. سجل التوزيعات (10 سنوات)
                div_yrs = len(divs.groupby(divs.index.year).sum())
                rows_html += add_to_table("سجل التوزيع", f"{div_yrs} سنة", "> 10 سنوات", "جراهام: الاستمرارية لعقد من الزمن تثبت صلابة نموذج العمل في الأزمات العنيفة.", div_yrs >= 10)

                # 7. نمو التوزيعات (5 سنوات)
                y_divs = divs.groupby(divs.index.year).sum()
                growth = ((y_divs.iloc[-1] / y_divs.iloc[-5]) - 1) * 100 if len(y_divs) >= 5 else 0
                rows_html += add_to_table("نمو التوزيعات", f"{growth:.1f}%", "> 0%", "لينش: نمو التوزيع السنوي هو الدرع الحقيقي لمحفظتك ضد التضخم العالمي.", growth > 0)

                # 8. التدفق النقدي الحر (FCF)
                fcf = cf.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cf.index else 0
                rows_html += add_to_table("التدفق النقدي (FCF)", "إيجابي" if fcf > 0 else "سلبي", "موجب (+)", "بافيت: الأرباح الحقيقية هي التي تتحول لنقد في البنك لا مجرد أرقام دفترية.", fcf > 0)

                # 9. سجل الأرباح (10 سنوات)
                net_inc = fin.loc['Net Income'].dropna() if 'Net Income' in fin.index else []
                profit_safe = (pd.Series(net_inc) > 0).all()
                rows_html += add_to_table("سجل الربحية", "مستقر" if profit_safe else "متذبذب", "أرباح مستمرة", "بافيت: نبتعد عن الشركات التي تخسر؛ الاستقرار هو مفتاح الأمان الاستثماري.", profit_safe)

                # 10. السيولة الجارية
                cr = info.get('currentRatio', 0) or 1.5
                rows_html += add_to_table("السيولة (Current)", f"{cr:.2f}", "> 1.5", "الأمان: توفر السيولة لسداد الالتزامات دون الحاجة لتسييل الأصول أو الاقتراض.", cr >= 1.5)

                # --- عرض النتائج النهائية ---
                st.subheader(f"💎 تقرير التدقيق الشامل لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                status_text = "🏆 سهم أرستقراطي ذهبي" if score >= 8 else "🟡 سهم عوائد جيد" if score >= 5 else "🔴 فخ عائد - مخاطرة عالية"
                status_color = "#03dac6" if score >= 8 else "#bb86fc" if score >= 5 else "#cf6679"
                st.markdown(f"<div class='status-box' style='color:{status_color};'>{status_text} ({score}/10)</div>", unsafe_allow_html=True)
                if score >= 8: st.balloons()

                # عرض الجدول المطور
                table_body = f"""
                <table class='styled-table'>
                    <thead><tr><th>المؤشر المالي</th><th>النتيجة الفعلية</th><th>المعيار المطلوب</th><th>الفلسفة الاستثمارية</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """
                st.markdown(table_body, unsafe_allow_html=True)

        except Exception as e: st.error(f"⚠️ خطأ تقني في جلب البيانات: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO - THE ULTIMATE ELITE EDITION 2026</p>", unsafe_allow_html=True)
