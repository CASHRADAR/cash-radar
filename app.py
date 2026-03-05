import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Dark UI + Neon Tail)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; border-bottom: 4px solid transparent; }
    
    /* ذيل النيون */
    .row-pass { border-bottom: 4px solid #00ff41 !important; box-shadow: 0 4px 10px rgba(0, 255, 65, 0.2); }
    .row-fail { border-bottom: 4px solid #ff003c !important; box-shadow: 0 4px 10px rgba(255, 0, 60, 0.2); }
    
    .pass-text { color: #00ff41; font-weight: bold; }
    .fail-text { color: #ff003c; font-weight: bold; }
    .desc-text { color: #a0a0a0; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة ذكاء القطاعات
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 2.5, 'roe_min': 15, 'note': "💡 قطاع مالي: السيولة تتبع معايير البنك المركزي والديون هي ودائع تشغيلية."},
    'Technology': {'pe_limit': 25, 'de_limit': 0.4, 'roe_min': 20, 'note': "🚀 تقنية: نركز على انعدام الديون وكفاءة الإدارة العالية جداً."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'roe_min': 8, 'note': "🏠 عقار: التوزيع المرتفع (90%+) هو معيار النجاح في الريتات."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'roe_min': 15, 'note': "⚖️ معايير قياسية: الالتزام الصارم بمدرسة القيمة (بافيت وجراهام)."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 2222):", "2222")
    scan_btn = st.button("تفعيل المسح الراداري ✨")

# دالة ذكية لجلب البيانات من القوائم المالية بمرونة
def get_val(df, keys):
    if df is None or df.empty: return 0
    for key in keys:
        match = [idx for idx in df.index if key.lower() in idx.lower().replace(" ", "")]
        if match: return df.loc[match[0]].iloc[0]
    return 0

if scan_btn:
    with st.spinner("جاري فحص النظم المالية وتدقيق سجل 10 سنوات..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info, fin, divs, cf = stock.info, stock.financials, stock.dividends, stock.cashflow

            if 'regularMarketPrice' in info or 'currentPrice' in info:
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                if 'REIT' in info.get('industry', ''): logic = SECTOR_DATA['Real Estate']

                score = 0
                rows_html = ""

                def add_row(name, result, criteria, philosophy, is_pass):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"<tr class='{s_class}'><td><b>{name}</b></td><td class='{t_class}'>{icon} {result}</td><td>{criteria}</td><td class='desc-text'>{philosophy}</td></tr>"

                # 1. المكرر التشغيلي
                op_inc = get_val(fin, ['OperatingIncome', 'Operating Income'])
                shares = info.get('sharesOutstanding', 1)
                pe_op = price / (op_inc / shares) if op_inc > 0 else (info.get('trailingPE', 0))
                rows_html += add_row("المكرر التشغيلي", f"{pe_op:.2f}", f"< {logic['pe_limit']}", "جراهام: نشتري الأرباح التشغيلية الحقيقية لضمان هامش الأمان السعري.", 0 < pe_op <= logic['pe_limit'])

                # 2. عائد التوزيع الحقيقي (يدوي)
                one_year_ago = datetime.now() - timedelta(days=365)
                real_divs = divs[divs.index > one_year_ago].sum() if not divs.empty else 0
                r_yield = (real_divs / price) * 100
                rows_html += add_row("عائد التوزيع الحقيقي", f"{r_yield:.2f}%", "> 4%", "لينش: العائد النقدي هو البرهان المادي الوحيد على ربحية الشركة.", r_yield >= 4.0)

                # 3. نسبة التوزيع (Payout)
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                p_pass = 20 <= payout <= 75 if sector != 'Real Estate' else 70 <= payout <= 95
                rows_html += add_row("نسبة التوزيع (Payout)", f"{payout:.1f}%", "20% - 75%", "المعيار: النسبة المتزنة تضمن استمرار التوزيع حتى في سنوات الركود.", p_pass)

                # 4. كفاءة الإدارة (ROE)
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                rows_html += add_row("كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"> {logic['roe_min']}%", "بافيت: قدرة الإدارة على تنمية أموال المساهمين ذاتهم ببراعة.", roe >= logic['roe_min'])

                # 5. نسبة الديون (D/E)
                de = (info.get('debtToEquity', 0) or 0) / 100
                rows_html += add_row("نسبة الديون", f"{de:.2f}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة.", de <= logic['de_limit'])

                # 6. سجل التوزيعات
                div_yrs = len(divs.groupby(divs.index.year).sum())
                rows_html += add_row("سجل التوزيع", f"{div_yrs} سنة", "> 10 سنوات", "جراهام: الاستمرارية لعقد تثبت صلابة العمل في أقسى الظروف.", div_yrs >= 10)

                # 7. نمو التوزيعات
                y_divs = divs.groupby(divs.index.year).sum()
                growth = ((y_divs.iloc[-1] / y_divs.iloc[-5]) - 1) * 100 if len(y_divs) >= 5 and y_divs.iloc[-5] > 0 else 0
                rows_html += add_row("نمو التوزيعات", f"{growth:.1f}%", "> 0%", "لينش: نمو التوزيع السنوي هو الدرع الحقيقي ضد التضخم العالمي.", growth > 0)

                # 8. التدفق النقدي (FCF)
                fcf = get_val(cf, ['FreeCashFlow', 'Free Cash Flow'])
                rows_html += add_row("التدفق النقدي (FCF)", "إيجابي" if fcf > 0 else "سلبي", "موجب (+)", "بافيت: الكاش الفعلي هو ما يدفع التوزيعات وليس الأرباح الدفترية.", fcf > 0)

                # 9. سجل الأرباح
                net_inc_val = get_val(fin, ['NetIncome', 'Net Income'])
                rows_html += add_row("سجل الربحية", "مستقر" if net_inc_val > 0 else "متذبذب", "أرباح موجبة", "بافيت: نبتعد عن الشركات الخاسرة؛ الاستقرار هو مفتاح الأمان.", net_inc_val > 0)

                # 10. السيولة الجارية
                cr = info.get('currentRatio', 0) or 1.5
                rows_html += add_row("السيولة (Current)", f"{cr:.2f}", "> 1.5", "الأمان: توفر الكاش لسداد الالتزامات دون بيع أصول الشركة.", cr >= 1.5)

                # --- العرض النهائي ---
                st.subheader(f"💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
                st.info(logic['note'])

                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 8 else "🟡 سهم عوائد جيد" if score >= 5 else "🔴 فخ عائد - مخاطرة عالية"
                s_color = "#00ff41" if score >= 8 else "#bb86fc" if score >= 5 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{s_text} ({score}/10)</div>", unsafe_allow_html=True)
                if score >= 8: st.balloons()

                st.markdown(f"<table class='styled-table'><thead><tr><th>المؤشر المالي</th><th>النتيجة الفعلية</th><th>المعيار المطلوب</th><th>الفلسفة الاستثمارية</th></tr></thead><tbody>{rows_html}</tbody></table>", unsafe_allow_html=True)

        except Exception as e: st.error(f"⚠️ خطأ تقني في جلب البيانات: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO - ULTIMATE STABLE EDITION 2026</p>", unsafe_allow_html=True)
