import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات المنصة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Purple Neon UI)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; font-size: 1.1em; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; border-bottom: 4px solid transparent; }
    .row-pass { border-bottom: 4px solid #00ff41 !important; box-shadow: 0 4px 10px rgba(0, 255, 65, 0.2); }
    .row-fail { border-bottom: 4px solid #ff003c !important; box-shadow: 0 4px 10px rgba(255, 0, 60, 0.2); }
    .pass-text { color: #00ff41; font-weight: bold; }
    .fail-text { color: #ff003c; font-weight: bold; }
    .source-link { color: #bb86fc; text-decoration: none; font-size: 0.85em; border: 1px solid #bb86fc; padding: 2px 8px; border-radius: 5px; }
    .source-link:hover { background: #bb86fc; color: #000; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة ذكاء القطاعات
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 8.0, 'payout': 20, 'roe': 15, 'note': "💡 قطاع مالي: الودائع هي وقود العمل، المديونية هنا تتبع معايير SAMA."},
    'Technology': {'pe_limit': 25, 'de_limit': 0.4, 'payout': 20, 'roe': 20, 'note': "🚀 تقنية: الأصول غير ملموسة، لذا نشترط انعدام الديون وكفاءة ROE عالية."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'payout': 70, 'roe': 8, 'note': "🏠 عقار (ريت): التوزيعات إلزامية، والديون طبيعية لنمو الأصول."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'payout': 20, 'roe': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة (بافيت وجراهام)."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم الذكي</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 1150):", "1150")
    scan_btn = st.button("تفعيل المسح الشامل 🚀")

if scan_btn:
    with st.spinner("جاري ربط الرادار بالمصادر الرسمية وفحص البيانات..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            divs = stock.dividends
            
            # روابط المصادر الذكية
            tada_url = f"https://www.saudiexchange.sa{symbol}"
            argaam_url = f"https://www.argaam.com{symbol}"

            if 'currentPrice' in info or 'regularMarketPrice' in info:
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])

                score = 0
                rows_html = ""

                def add_row(name, result, criteria, explanation, is_pass, source_type):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    # اختيار الرابط المناسب (تداول للقوائم، أرقام للمؤشرات التاريخية)
                    link = tada_url if source_type == "tadawul" else argaam_url
                    source_btn = f"<a href='{link}' target='_blank' class='source-link'>المصدر 🔗</a>"
                    return f"<tr class='{s_class}'><td><b>{name}</b></td><td class='{t_class}'>{icon} {result}</td><td>{criteria}</td><td style='font-size:0.85em; color:#aaa;'>{explanation}</td><td>{source_btn}</td></tr>"

                # الحسابات
                pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))
                if not divs.empty:
                    tz = divs.index.tz
                    one_year_ago = datetime.now(tz) - timedelta(days=365)
                    real_divs = divs[divs.index > one_year_ago].sum()
                else: real_divs = 0
                r_yield = (real_divs / price) * 100
                payout = (info.get('payoutRatio', 0) or 0) * 100
                if payout > 100: payout /= 100
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                de_ratio = (info.get('debtToEquity', 0) or 0) / 100

                # بناء التقرير
                rows_html += add_row("مكرر الربحية (P/E)", f"{pe_val:.2f}", f"< {logic['pe_limit']}", "السعر المدفوع مقابل الربح؛ جراهام يفضل الرخص السعري.", 0 < pe_val <= logic['pe_limit'], "argaam")
                rows_html += add_row("عائد التوزيع الحقيقي", f"{r_yield:.2f}%", "> 4%", "النقد المستلم فعلياً؛ نبحث عن دخل يتفوق على التضخم.", r_yield >= 4.0, "tadawul")
                rows_html += add_row("نسبة التوزيع (Payout)", f"{payout:.1f}%", f"{logic['payout']}-75%", "توازن المكافأة والنمو؛ النسبة العالية جداً خطر.", logic['payout'] <= payout <= 75, "tadawul")
                rows_html += add_row("كفاءة الإدارة (ROE)", f"{roe:.1f}%", "> 15%", "بصمة بافيت؛ قدرة الإدارة على تنمية أموال المساهمين.", roe >= 15, "argaam")
                rows_html += add_row("نسبة المديونية (D/E)", f"{de_ratio:.2f}", f"< {logic['de_limit']}", "الملاءة؛ الديون المنخفضة تحمي الشركة من تقلب الفائدة.", de_ratio <= logic['de_limit'], "tadawul")
                rows_html += add_row("سجل التوزيع", f"{len(divs.groupby(divs.index.year).sum())} سنة", "> 10 سنوات", "الاستمرارية التاريخية هي برهان قوة نموذج العمل.", len(divs.groupby(divs.index.year).sum()) >= 10, "argaam")
                rows_html += add_row("السيولة (Current)", f"{info.get('currentRatio', 1.5):.2f}", "> 1.2", "توفر الكاش لسداد الالتزامات دون بيع أصول الشركة.", info.get('currentRatio', 1.5) >= 1.2, "tadawul")

                # العرض النهائي
                st.subheader(f"💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 6 else "🟡 سهم عوائد جيد" if score >= 4 else "🔴 فخ عائد"
                s_color = "#00ff41" if score >= 6 else "#bb86fc" if score >= 4 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{s_text} ({score}/7)</div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <table class='styled-table'>
                    <thead>
                        <tr><th>المؤشر المالي</th><th>النتيجة</th><th>المعيار</th><th>الفلسفة</th><th>المصدر الرسمي</th></tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ حدث خطأ: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO | OFFICIAL SOURCE EDITION 2026</p>", unsafe_allow_html=True)

