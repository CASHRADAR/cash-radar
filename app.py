import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO | Stable Edition", page_icon="📡", layout="wide")

# 2. تصميم الواجهة الاحترافية (Luxury Dark Purple)
st.markdown("""
    <style>
    .stApp { background-color: #08080c; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 15px rgba(187, 134, 252, 0.5); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: 800; margin: 20px 0; background: #161620; border: 2px solid #3700b3; }
    .styled-table { width: 100%; border-collapse: collapse; margin: 25px 0; border-radius: 10px; overflow: hidden; background: #1a1a24; }
    .styled-table thead tr { background-color: #4a148c; color: #bb86fc; text-align: right; }
    .styled-table th, .styled-table td { padding: 15px 20px; border-bottom: 1px solid #252535; text-align: right; }
    .pass-val { color: #03dac6; font-weight: bold; }
    .fail-val { color: #cf6679; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة بيانات القطاعات
SECTOR_DATA = {
    'Financial Services': {'pe_avg': 16, 'de_limit': 2.5, 'payout_avg': 55, 'roe_avg': 15, 'note': "💡 قطاع مالي: السيولة تتبع معايير SAMA والودائع تُحسب كديون تشغيلية."},
    'Technology': {'pe_avg': 28, 'de_limit': 0.4, 'payout_avg': 40, 'roe_avg': 20, 'note': "🚀 تقنية: نركز على انعدام الديون وكفاءة الإدارة العالية."},
    'Real Estate': {'pe_avg': 22, 'de_limit': 1.1, 'payout_avg': 90, 'roe_avg': 8, 'note': "🏠 عقار: التوزيع المرتفع (90%+) هو معيار الأمان في الريتات."},
    'Utilities': {'pe_avg': 15, 'de_limit': 1.4, 'payout_avg': 65, 'roe_avg': 10, 'note': "⚡ مرافق: استقرار التدفقات النقدية يسمح بمديونية أعلى قليلاً."},
    'Default': {'pe_avg': 18, 'de_limit': 0.6, 'payout_avg': 55, 'roe_avg': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة (بافيت وجراهام)."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 2222):", "2222")
    scan_btn = st.button("تفعيل المسح الاحترافي ✨")

if scan_btn:
    with st.spinner("جاري فحص النظم المالية وتدقيق سجل 10 سنوات..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            fin = stock.financials
            divs = stock.dividends

            if 'regularMarketPrice' in info:
                price = info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                score = 0
                table_rows = []

                # --- دالة مساعدة لجلب البيانات من القوائم المالية بأمان ---
                def get_fin_val(df, label):
                    if df is not None and not df.empty:
                        # البحث عن المسمى بمرونة (مع مسافات أو بدون)
                        match = [idx for idx in df.index if label.lower() in idx.lower().replace(" ", "")]
                        if match: return df.loc[match[0]].iloc[0]
                    return 0

                # 1. المكرر التشغيلي (P/E)
                op_income = get_fin_val(fin, 'OperatingIncome')
                shares = info.get('sharesOutstanding', 1)
                pe_op = price / (op_income / shares) if op_income > 0 else 0
                is_pass = 0 < pe_op <= 15
                if is_pass: score += 1
                table_rows.append([ "📈 المكرر التشغيلي", f"{pe_op:.2f}", f"{logic['pe_avg']}", "< 15", "جراهام: نشتري الربح الفعلي بسعر عادل لضمان هامش الأمان.", is_pass])

                # 2. عائد التوزيع الحقيقي (يدوي 365 يوم)
                real_div_sum = divs.last('365D').sum() if not divs.empty else 0
                real_yield = (real_div_sum / price) * 100
                is_pass = real_yield >= 4.0
                if is_pass: score += 1
                table_rows.append(["💰 عائد التوزيع", f"{real_yield:.2f}%", "4.5%", "> 4%", "لينش: العائد النقدي هو الدليل المادي على جودة أرباح الشركة.", is_pass])

                # 3. نسبة التوزيع (Payout)
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                is_pass = 20 <= payout <= 70 if sector != 'Real Estate' else 70 <= payout <= 95
                if is_pass: score += 1
                table_rows.append(["⚖️ نسبة التوزيع", f"{payout:.1f}%", f"{logic['payout_avg']}%", "20-70%", "المعيار: التوزيع المتزن يحمي الشركة من التعثر في سنوات الركود.", is_pass])

                # 4. كفاءة الإدارة (ROE)
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                is_pass = roe >= logic['roe_avg']
                if is_pass: score += 1
                table_rows.append(["🚀 كفاءة الإدارة", f"{roe:.1f}%", f"{logic['roe_avg']}%", f"> {logic['roe_avg']}%", "بافيت: أهم مقياس لقدرة الشركة على تنمية أموال المساهمين.", is_pass])

                # 5. نسبة الديون (D/E)
                de = (info.get('debtToEquity', 0) or 0) / 100
                is_pass = de <= logic['de_limit']
                if is_pass: score += 1
                table_rows.append(["🛡️ نسبة الديون", f"{de:.2f}", f"< {logic['de_limit']}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة.", is_pass])

                # 6. سجل التوزيعات (سنوات)
                div_yrs = len(divs.groupby(divs.index.year).sum())
                is_pass = div_yrs >= 10
                if is_pass: score += 1
                table_rows.append(["📅 سجل التوزيع", f"{div_yrs} سنة", "10+ سنوات", "> 10 سنوات", "جراهام: الاستمرارية لعقد تثبت متانة العمل في الأزمات.", is_pass])

                # --- العرض النهائي ---
                st.subheader(f"💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                status_color = "#03dac6" if score >= 6 else "#bb86fc" if score >= 4 else "#cf6679"
                status_text = "سهم أرستقراطي ذهبي" if score >= 6 else "سهم عوائد جيد" if score >= 4 else "فخ عائد - مخاطرة عالية"
                st.markdown(f"<div class='status-box' style='color:{status_color};'>{status_text} ({score}/6)</div>", unsafe_allow_html=True)
                if score >= 6: st.balloons()

                # بناء الجدول بصيغة HTML
                rows_html = ""
                for r in table_rows:
                    cls = "pass-val" if r[5] else "fail-val"
                    icon = "✅" if r[5] else "❌"
                    rows_html += f"<tr><td>{r[0]}</td><td class='{cls}'>{icon} {r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"

                st.markdown(f"""
                <table class='styled-table'>
                    <thead><tr><th>المؤشر المالي</th><th>النتيجة الفعلية</th><th>متوسط القطاع</th><th>المعيار المطلوب</th><th>الفلسفة الاستثمارية</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """, unsafe_allow_html=True)
            else: st.error("❌ تعذر جلب البيانات. الرمز قد يكون غير صحيح أو بياناته غير متوفرة حالياً.")
        except Exception as e: st.error(f"⚠️ خطأ تقني: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO - 2026 STABLE VERSION</p>", unsafe_allow_html=True)
