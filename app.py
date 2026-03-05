import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Neon UI)
st.markdown("""
    <style>
    .stApp { background-color: #050508; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.6); text-align: center; font-weight: 800; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.8em; font-weight: bold; margin-bottom: 30px; background: #111118; border: 2px solid #3700b3; }
    .styled-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; margin-top: 20px; }
    .styled-table thead tr { background-color: #1a1a24; color: #bb86fc; }
    .styled-table th { padding: 15px; text-align: right; border-bottom: 2px solid #3700b3; }
    .styled-table td { padding: 15px; background-color: #161620; vertical-align: middle; border-bottom: 4px solid transparent; }
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
    'Financial Services': {'pe_limit': 15, 'de_limit': 2.5, 'roe_min': 15, 'op_margin_min': 25},
    'Technology': {'pe_limit': 25, 'de_limit': 0.4, 'roe_min': 20, 'op_margin_min': 15},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'roe_min': 8, 'op_margin_min': 40},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'roe_min': 15, 'op_margin_min': 10}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم التشغيلي</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 2222):", "2222")
    scan_btn = st.button("تفعيل المسح الراداري ✨")

if scan_btn:
    with st.spinner("جاري حل تعارض المناطق الزمنية وتدقيق البيانات التشغيلية..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            divs = stock.dividends

            if 'currentPrice' in info or 'regularMarketPrice' in info:
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                
                score = 0
                rows_html = ""

                def add_row(name, result, criteria, philosophy, is_pass):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"<tr class='{s_class}'><td><b>{name}</b></td><td class='{t_class}'>{icon} {result}</td><td>{criteria}</td><td class='desc-text'>{philosophy}</td></tr>"

                # --- 1. إصلاح مشكلة التوزيعات (توحيد التوقيت) ---
                if not divs.empty:
                    # تحويل الوقت الحالي لنفس منطقة زمنية البيانات (الرياض)
                    tz = divs.index.tz
                    one_year_ago = datetime.now(tz) - timedelta(days=365)
                    real_divs = divs[divs.index > one_year_ago].sum()
                else:
                    real_yield = 0
                    real_divs = 0
                
                real_yield = (real_divs / price) * 100 if price > 0 else 0

                # --- 2. مكرر الربحية التشغيلي والهوامش ---
                op_margin = (info.get('operatingMargins', 0) or 0) * 100
                pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))

                # --- 3. بناء الجدول التشغيلي الكامل ---
                rows_html += add_row("المكرر التشغيلي", f"{pe_val:.2f}", f"< {logic['pe_limit']}", "جراهام: نشتري الربح التشغيلي الحقيقي لضمان هامش الأمان السعري.", 0 < pe_val <= logic['pe_limit'])
                rows_html += add_row("الهامش التشغيلي", f"{op_margin:.1f}%", f"> {logic['op_margin_min']}%", "بافيت: يعكس كفاءة الشركة في تحويل المبيعات إلى ربح حقيقي.", op_margin >= logic['op_margin_min'])
                rows_html += add_row("عائد التوزيع الحقيقي", f"{real_yield:.2f}%", "> 4%", "لينش: العائد النقدي الفعلي هو الدليل المادي الوحيد على جودة الأرباح.", real_yield >= 4.0)
                
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                rows_html += add_row("نسبة التوزيع (Payout)", f"{payout:.1f}%", "20% - 75%", "المعيار: النسبة المتزنة تضمن استقرار التوزيع وتدعم نمو الشركة.", 20 <= payout <= 75)

                roe = (info.get('returnOnEquity', 0) or 0) * 100
                rows_html += add_row("كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"> {logic['roe_min']}%", "بافيت: قدرة الإدارة على تنمية أموال المساهمين ذاتهم ببراعة.", roe >= logic['roe_min'])

                de = (info.get('debtToEquity', 0) or 0) / 100
                rows_html += add_row("نسبة الديون (D/E)", f"{de:.2f}", f"< {logic['de_limit']}", "الملاءة: الديون المنخفضة تمنح الشركة حصانة ضد تقلبات الفائدة.", de <= logic['de_limit'])

                div_yrs = len(divs.groupby(divs.index.year).sum())
                rows_html += add_row("سجل التوزيع", f"{div_yrs} سنة", "> 10 سنوات", "جراهام: الاستمرارية لعقد تثبت صلابة العمل في أقسى الظروف.", div_yrs >= 10)

                # --- 4. العرض النهائي الفخم ---
                st.subheader(f"💎 تقرير التدقيق التشغيلي: {info.get('longName', symbol)}")
                
                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 6 else "🟡 سهم عوائد جيد" if score >= 4 else "🔴 فخ عائد - مخاطرة عالية"
                s_color = "#00ff41" if score >= 6 else "#bb86fc" if score >= 4 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{status_text if 'status_text' in locals() else s_text} ({score}/7)</div>", unsafe_allow_html=True)
                if score >= 6: st.balloons()

                st.markdown(f"<table class='styled-table'><thead><tr><th>المؤشر المالي</th><th>النتيجة الفعلية</th><th>المعيار المطلوب</th><th>الفلسفة الاستثمارية</th></tr></thead><tbody>{rows_html}</tbody></table>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ حدث خطأ تقني: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO | BUG FIXED EDITION 2026</p>", unsafe_allow_html=True)
