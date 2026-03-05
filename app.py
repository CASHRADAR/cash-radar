import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO | Elite Edition", page_icon="📡", layout="wide")

# 2. واجهة المستخدم البنفسجية المتطورة (Luxury Grid UI)
st.markdown("""
    <style>
    .stApp { background-color: #08080c; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 15px rgba(187, 134, 252, 0.5); text-align: center; font-weight: 800; }
    .status-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: 800; margin: 20px 0; background: #161620; border: 2px solid #3700b3; }
    
    /* تصميم الجدول التنفيذي */
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95em; border-radius: 10px; overflow: hidden; background: #1a1a24; }
    .styled-table thead tr { background-color: #4a148c; color: #bb86fc; text-align: right; font-weight: bold; }
    .styled-table th, .styled-table td { padding: 15px 20px; border-bottom: 1px solid #252535; text-align: right; }
    .styled-table tbody tr:hover { background-color: rgba(187, 134, 252, 0.05); }
    .pass-val { color: #03dac6; font-weight: bold; }
    .fail-val { color: #cf6679; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")
st.markdown("<p style='text-align: center; color: #888;'>إصدار التدقيق المالي المتطور - تحليل النخبة للسوق السعودي</p>", unsafe_allow_html=True)

# 3. مصفوفة القطاعات المحدثة (مقرونة بمتوسطات السوق التقديرية)
SECTOR_DATA = {
    'Financial Services': {'pe_avg': 16.5, 'de_limit': 2.0, 'payout_avg': 55, 'roe_avg': 16, 'note': "💡 قطاع مالي: السيولة تتبع معايير SAMA."},
    'Technology': {'pe_avg': 28.0, 'de_limit': 0.35, 'payout_avg': 40, 'roe_avg': 22, 'note': "🚀 تقنية: نركز على انعدام الديون وكفاءة الإدارة (ROE)."},
    'Real Estate': {'pe_avg': 22.0, 'de_limit': 1.0, 'payout_avg': 90, 'roe_avg': 9, 'note': "🏠 عقار: التوزيع المرتفع (90%+) هو معيار النجاح."},
    'Utilities': {'pe_avg': 14.0, 'de_limit': 1.3, 'payout_avg': 65, 'roe_avg': 11, 'note': "⚡ مرافق: الاستقرار النقدي يسمح بديون أعلى قليلاً."},
    'Energy': {'pe_avg': 15.0, 'de_limit': 0.7, 'payout_avg': 60, 'roe_avg': 18, 'note': "⛽ طاقة: نركز على العائد المستدام والمكرر المنخفض."},
    'Default': {'pe_avg': 18.0, 'de_limit': 0.5, 'payout_avg': 50, 'roe_avg': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح الاحترافي ✨")

if scan_btn:
    with st.spinner("جاري إجراء المسح العشري وتدقيق القوائم المالية..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        try:
            info, fin, divs = stock.info, stock.financials, stock.dividends
            if 'regularMarketPrice' in info:
                price = info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                score = 0
                rows = []

                # --- دالة إضافة البيانات المنظمة ---
                def add_row(icon, name, result, sector_avg, criteria, philosophy, is_pass):
                    global score
                    if is_pass: score += 1
                    status_class = "pass-val" if is_pass else "fail-val"
                    icon_status = "✅" if is_pass else "❌"
                    rows.append(f"""
                        <tr>
                            <td>{icon} {name}</td>
                            <td class='{status_class}'>{icon_status} {result}</td>
                            <td>{sector_avg}</td>
                            <td>{criteria}</td>
                            <td>{philosophy}</td>
                        </tr>
                    """)

                # 1. المكرر التشغيلي (صارم < 15)
                op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
                pe_op = price / (op_inc / info.get('sharesOutstanding', 1)) if op_inc > 0 else 0
                add_row("📈", "المكرر التشغيلي", f"{pe_op:.2f}", f"{logic['pe_avg']}", "< 15 (أمان)", "جراهام: نشتري الربح التشغيلي الحقيقي بسعر رخيص لضمان هامش الأمان.", 0 < pe_op <= 15)

                # 2. العائد الحقيقي (يدوي)
                real_yield = (divs.last('365D').sum() / price) * 100 if not divs.empty else 0
                add_row("💰", "عائد التوزيع", f"{real_yield:.2f}%", "4.5%", "> 4%", "لينش: العائد النقدي هو الدليل الملموس على صدق أرباح الشركة ومكافأة المستثمر.", real_yield >= 4.0)

                # 3. نسبة التوزيع (Payout)
                payout = (info.get('payoutRatio', 0) or 0) * 100
                if payout > 100: payout /= 100
                add_row("⚖️", "نسبة التوزيع", f"{payout:.1f}%", f"{logic['payout_avg']}%", "20% - 70%", "المعيار: النسبة المتزنة تحمي التوزيعات من القطع وتسمح للشركة بالنمو الذاتي.", 20 <= payout <= 75 if sector != 'Real Estate' else 70 <= payout <= 95)

                # 4. كفاءة الإدارة (ROE)
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                add_row("🚀", "كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"{logic['roe_avg']}%", f"> {logic['roe_avg']}%", "بافيت: قدرة الإدارة على توليد ثروة من كل ريال يملكه المساهمون.", roe >= logic['roe_avg'])

                # 5. نسبة الديون (D/E)
                de = (info.get('debtToEquity', 0) or 0) / 100
                add_row("🛡️", "نسبة الديون", f"{de:.2f}", f"< {logic['de_limit']}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة البنكية.", de <= logic['de_limit'])

                # 6. استمرارية التوزيع
                div_yrs = len(divs.groupby(divs.index.year).sum())
                add_row("📅", "سجل التوزيع", f"{div_yrs} سنة", "10+ سنوات", "> 10 سنوات", "جراهام: الاستمرارية لعقد من الزمن تثبت صلابة نموذج العمل في الأزمات.", div_yrs >= 10)

                # 7. السيولة (Current Ratio)
                cr = info.get('currentRatio', 0) or 1.5
                add_row("💧", "نسبة السيولة", f"{cr:.2f}", "1.5", "> 1.5", "الأمان: توفر الكاش لسداد الالتزامات دون الحاجة لتسييل الأصول.", cr >= 1.5)

                # --- عرض النتائج ---
                st.subheader(f"💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                if score >= 6:
                    st.markdown(f"<div class='status-box' style='color:#03dac6;'>🏆 التصنيف: سهم أرستقراطي ذهبي ({score}/7)</div>", unsafe_allow_html=True); st.balloons()
                elif score >= 4:
                    st.markdown(f"<div class='status-box' style='color:#bb86fc;'>🟡 التصنيف: سهم عوائد جيد ({score}/7)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='status-box' style='color:#cf6679;'>🔴 التصنيف: فخ عائد - مخاطرة عالية ({score}/7)</div>", unsafe_allow_html=True)

                # إنشاء الجدول HTML
                table_html = f"""
                <table class='styled-table'>
                    <thead>
                        <tr>
                            <th>المؤشر المالي</th>
                            <th>النتيجة الفعلية</th>
                            <th>متوسط القطاع</th>
                            <th>المعيار المطلوب</th>
                            <th>الفلسفة الاستثمارية</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)
            else: st.error("❌ فشل المسح: تعذر الوصول للبيانات.")
        except Exception as e: st.error(f"⚠️ خطأ تقني: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO - ULTIMATE INVESTOR EDITION 2026</p>", unsafe_allow_html=True)
