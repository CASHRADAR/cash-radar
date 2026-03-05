import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة الاحترافية (Luxury Purple Neon)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    
    /* تصميم الجدول التنفيذي المطور */
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; font-size: 1.1em; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; border-bottom: 4px solid transparent; }
    
    /* ذيل النيون للنتائج */
    .row-pass { border-bottom: 4px solid #00ff41 !important; box-shadow: 0 4px 10px rgba(0, 255, 65, 0.2); }
    .row-fail { border-bottom: 4px solid #ff003c !important; box-shadow: 0 4px 10px rgba(255, 0, 60, 0.2); }
    
    .pass-text { color: #00ff41; font-weight: bold; }
    .fail-text { color: #ff003c; font-weight: bold; }
    .desc-text { color: #a0a0a0; font-size: 0.9em; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة ذكاء القطاعات (تعديل المعايير للبنوك والريتات)
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 8.0, 'payout': [20, 75], 'note': "💡 ملاحظة: في قطاع البنوك، الودائع تُمثل المديونية التشغيلية، والرافعة المرتفعة طبيعية ومقبولة."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'payout': [70, 95], 'note': "🏠 ملاحظة: الريتات توزع 90%+ نظاماً، والدين وسيلة لتمويل الأصول المدرة للدخل."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'payout': [20, 70], 'note': "⚖️ ملاحظة: نطبق المعايير الصارمة للقيمة لضمان أقصى درجات الأمان المالي."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 لوحة التحكم الذكية</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 1150):", "1150")
    scan_btn = st.button("بدء المسح الراداري 🚀")

if scan_btn:
    with st.spinner("جاري تدقيق البيانات المالية وتوليد الشرح الفلسفي..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            bs = stock.balance_sheet
            divs = stock.dividends

            if 'currentPrice' in info or 'regularMarketPrice' in info:
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                # --- محرك الحسابات الذكي ---
                # 1. الديون للبنوك
                de_ratio = (info.get('debtToEquity', 0) or 0) / 100
                if de_ratio == 0 and sector == 'Financial Services':
                    total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
                    total_equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 1
                    de_ratio = total_liab / total_equity if total_equity > 0 else 0

                # 2. المكرر والعائد
                pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))
                real_divs = divs.last('365D').sum() if not divs.empty else 0
                r_yield = (real_divs / price) * 100
                payout = (info.get('payoutRatio', 0) or 0) * 100
                if payout > 100: payout /= 100
                roe = (info.get('returnOnEquity', 0) or 0) * 100

                score = 0
                rows_html = ""

                def add_row(name, result, criteria, explanation, is_pass):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"""
                    <tr class='{s_class}'>
                        <td><b>{name}</b></td>
                        <td class='{t_class}'>{icon} {result}</td>
                        <td>{criteria}</td>
                        <td class='desc-text'>{explanation}</td>
                    </tr>
                    """

                # تنفيذ المعايير مع الشرح المفصل
                rows_html += add_row("(P/E) مكرر الربحية", f"{pe_val:.2f}", f"< {logic['pe_limit']}", "يقيس السعر الذي تدفعه مقابل كل ريال من أرباح الشركة؛ المكرر المنخفض يعني أنك تشتري السهم بسعر عادل غير متضخم.", 0 < pe_val <= logic['pe_limit'])
                
                rows_html += add_row("عائد التوزيع الحقيقي", f"{r_yield:.2f}%", "> 4%", "هو النقد الفعلي الذي يدخل جيبك سنوياً؛ نبحث عن عائد يتفوق على التضخم والودائع البنكية التقليدية.", r_yield >= 4.0)
                
                rows_html += add_row("(Payout) نسبة التوزيع", f"{payout:.1f}%", f"{logic['payout'][0]}-{logic['payout'][1]}%", "توضح مقدار ما توزعه الشركة من صافي أرباحها؛ النسبة المتزنة تعني أن الشركة تكافئك وتحافظ على سيولة للنمو.", logic['payout'][0] <= payout <= logic['payout'][1])
                
                rows_html += add_row("(ROE) كفاءة الإدارة", f"{roe:.1f}%", "> 15%", "يقيس براعة الإدارة في توليد أرباح من أموال المساهمين؛ وارن بافيت يعتبر هذا المؤشر هو 'بصمة الجودة' في أي شركة.", roe >= 15)
                
                rows_html += add_row("(D/E) نسبة المديونية", f"{de_ratio:.2f}", f"< {logic['de_limit']}", "توضح حجم التزامات الشركة مقابل حقوق ملاكها؛ الديون المنخفضة تحمي الشركة من أخطار رفع الفائدة البنكية.", de_ratio <= logic['de_limit'])
                
                rows_html += add_row("سجل التوزيع", f"{len(divs.groupby(divs.index.year).sum())} سنة", "> 10 سنوات", "الاستمرارية التاريخية هي أكبر برهان على قوة المركز المالي وقدرة الشركة على تجاوز الأزمات الاقتصادية الصعبة.", len(divs.groupby(divs.index.year).sum()) >= 10)
                
                rows_html += add_row("(Current Ratio) السيولة", f"{info.get('currentRatio', 1.5):.2f}", "> 1.2", "تقيس قدرة الشركة على سداد ديونها قصيرة الأجل فوراً؛ السيولة العالية تعني أماناً تشغيلياً وعدم حاجة للاقتراض الطارئ.", info.get('currentRatio', 1.5) >= 1.2)

                # العرض النهائي
                st.subheader(f"💎 تحليل كاش رادار لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 6 else "🟡 سهم عوائد جيد" if score >= 4 else "🔴 فخ عائد - مخاطرة عالية"
                s_color = "#00ff41" if score >= 6 else "#bb86fc" if score >= 4 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{s_text} ({score}/7)</div>", unsafe_allow_html=True)
                if score >= 6: st.balloons()
                
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

        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO | PROFESSIONAL REPORT EDITION 2026</p>", unsafe_allow_html=True)
