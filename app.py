import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Purple Neon UI)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    
    /* تصميم الجدول التنفيذي المطور بالنيون */
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; font-size: 1.1em; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; border-bottom: 4px solid transparent; }
    
    /* ذيل النيون */
    .row-pass { border-bottom: 4px solid #00ff41 !important; box-shadow: 0 4px 10px rgba(0, 255, 65, 0.2); }
    .row-fail { border-bottom: 4px solid #ff003c !important; box-shadow: 0 4px 10px rgba(255, 0, 60, 0.2); }
    
    .pass-text { color: #00ff41; font-weight: bold; }
    .fail-text { color: #ff003c; font-weight: bold; }
    .desc-text { color: #a0a0a0; font-size: 0.85em; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة ذكاء القطاعات (معايير بافيت وجراهام المعدلة قطاعياً)
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 8.0, 'payout': [20, 80], 'roe': 15, 'note': "💡 قطاع مالي: الودائع تُحسب كالتزامات تشغيلية، والرافعة المالية العالية مقبولة."},
    'Technology': {'pe_limit': 25, 'de_limit': 0.4, 'payout': [10, 50], 'roe': 20, 'note': "🚀 تقنية: نركز على انعدام الديون وكفاءة الإدارة العالية جداً والنمو."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.2, 'payout': [70, 95], 'roe': 8, 'note': "🏠 عقار (ريت): التوزيع فوق 90% إلزامي نظاماً، والديون طبيعية لتمويل الأصول."},
    'Utilities': {'pe_limit': 15, 'de_limit': 1.5, 'payout': [50, 85], 'roe': 10, 'note': "⚡ مرافق: تدفقات نقدية مستقرة تسمح بمديونية أعلى قليلاً."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'payout': [20, 70], 'roe': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة (بافيت وجراهام)."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم الذكي</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح الشامل 🚀")

if scan_btn:
    with st.spinner("جاري تنقية البيانات وحساب المؤشرات التشغيلية..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            divs = stock.dividends
            
            if 'currentPrice' in info or 'regularMarketPrice' in info:
                # البيانات الأساسية
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                score = 0
                rows_html = ""

                # دالة إضافة الصفوف للجدول
                def add_row(name, result, criteria, explanation, is_pass):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"<tr class='{s_class}'><td><b>{name}</b></td><td class='{t_class}'>{icon} {result}</td><td>{criteria}</td><td class='desc-text'>{explanation}</td></tr>"

                # --- الحسابات المالية الدقيقة ---
                
                # 1. المكرر التشغيلي
                pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))
                rows_html += add_row("مكرر الربحية (P/E)", f"{pe_val:.2f}", f"< {logic['pe_limit']}", "جراهام: نشتري الأرباح التشغيلية بسعر عادل لضمان 'هامش الأمان' وتجنب الفقاعات.", 0 < pe_val <= logic['pe_limit'])

                # 2. عائد التوزيع (الحساب اليدوي لآخر سنة)
                if not divs.empty:
                    tz = divs.index.tz
                    one_year_ago = datetime.now(tz) - timedelta(days=365)
                    real_divs_sum = divs[divs.index > one_year_ago].sum()
                    r_yield = (real_divs_sum / price) * 100
                else: r_yield = 0
                rows_html += add_row("عائد التوزيع الحقيقي", f"{r_yield:.2f}%", "> 4%", "لينش: العائد النقدي هو البرهان المادي الوحيد على صدق أرباح الشركة ومكافأة المساهم.", r_yield >= 4.0)

                # 3. نسبة التوزيع (Payout)
                payout = (info.get('payoutRatio', 0) or 0) * 100
                if payout > 100: payout /= 100
                p_pass = logic['payout'][0] <= payout <= logic['payout'][1]
                rows_html += add_row("نسبة التوزيع (Payout)", f"{payout:.1f}%", f"{logic['payout'][0]}-{logic['payout'][1]}%", "المعيار: النسبة المتزنة تحمي التوزيعات من القطع وتسمح للشركة بإعادة الاستثمار للنمو.", p_pass)

                # 4. كفاءة الإدارة (ROE)
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                rows_html += add_row("كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"> {logic['roe']}%", "بافيت: يقيس مدى براعة الإدارة في توليد أرباح من كل ريال يملكه المساهمون.", roe >= logic['roe'])

                # 5. المديونية (D/E) - معالجة خاصة للبنوك
                de_ratio = (info.get('debtToEquity', 0) or 0) / 100
                if de_ratio == 0 and sector == 'Financial Services':
                    # حساب الرافعة المالية للبنوك يدوياً إذا لم يتوفر D/E
                    de_ratio = (info.get('bookValue', 1) / price) * 10 # تقدير تقريبي في حال نقص بيانات الميزانية
                rows_html += add_row("نسبة المديونية (D/E)", f"{de_ratio:.2f}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة البنكية وضغوط السداد.", de_ratio <= logic['de_limit'])

                # 6. استمرارية التوزيع (سنوات)
                div_yrs = len(divs.groupby(divs.index.year).sum())
                rows_html += add_row("سجل التوزيع التاريخي", f"{div_yrs} سنة", "> 10 سنوات", "جراهام: الاستمرارية لعقد من الزمن تثبت صلابة نموذج العمل وقدرته على تجاوز الأزمات.", div_yrs >= 10)

                # 7. السيولة الجارية
                cr = info.get('currentRatio', 1.5) or 1.5
                rows_html += add_row("نسبة السيولة (Current)", f"{cr:.2f}", "> 1.2", "الأمان: توفر الكاش لسداد الالتزامات قصيرة الأجل دون الحاجة للاقتراض الطارئ.", cr >= 1.2)

                # 8. جودة الأرباح (التدقيق التشغيلي)
                op_margin = (info.get('operatingMargins', 0) or 0) * 100
                rows_html += add_row("الهامش التشغيلي", f"{op_margin:.1f}%", "> 10%", "بافيت: يعكس قوة النشاط الأساسي للشركة بعيداً عن أي أرباح استثنائية أو عرضية.", op_margin >= 10)

                # 9. التدفق النقدي (FCF)
                fcf_status = "إيجابي" if (info.get('freeCashflow', 0) or 0) > 0 else "غير متوفر/سلبي"
                rows_html += add_row("التدفق النقدي (FCF)", fcf_status, "موجب (+)", "بافيت: الأرباح الحقيقية هي التي تتحول لنقد في البنك، وهي المصدر الفعلي للتوزيعات.", fcf_status == "إيجابي")

                # 10. نمو الأرباح (EPS Growth)
                eg = (info.get('earningsQuarterlyGrowth', 0) or 0) * 100
                rows_html += add_row("نمو الأرباح المستقبلي", f"{eg:.1f}%", "> 5%", "لينش: استمرار نمو الأرباح هو الوقود الذي يدفع سعر السهم وقيمة التوزيعات للأعلى.", eg >= 5)

                # --- العرض النهائي الفخم ---
                st.subheader(f"💎 تقرير التدقيق المالي لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 8 else "🟡 سهم عوائد جيد" if score >= 5 else "🔴 فخ عائد - مخاطرة عالية"
                s_color = "#00ff41" if score >= 8 else "#bb86fc" if score >= 5 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{s_text} ({score}/10)</div>", unsafe_allow_html=True)
                if score >= 8: st.balloons()

                st.markdown(f"""
                <table class='styled-table'>
                    <thead>
                        <tr>
                            <th>المؤشر المالي</th>
                            <th>النتيجة الفعلية</th>
                            <th>المعيار المطلوب</th>
                            <th>شرح المؤشر والمعيار (الفلسفة الاستثمارية)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                """, unsafe_allow_html=True)

            else:
                st.error("❌ تعذر جلب بيانات السهم. تأكد من الرمز (مثلاً: 1150 لإنماء، 2222 لأرامكو).")

        except Exception as e:
            st.error(f"⚠️ حدث خطأ تقني في الاتصال بمزود البيانات: {str(e)}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO | THE ULTIMATE ELITE EDITION 2026</p>", unsafe_allow_html=True)
