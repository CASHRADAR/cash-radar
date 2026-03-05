import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات المنصة
st.set_page_config(page_title="CASH RADAR PRO | Banking Logic", page_icon="📡", layout="wide")

# 2. تصميم الواجهة البنفسجية المتطورة
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
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة ذكاء القطاعات (معالجة البنوك والريتات)
SECTOR_DATA = {
    'Financial Services': {'pe_limit': 15, 'de_limit': 8.0, 'payout': [20, 75], 'note': "💡 ملاحظة: في البنوك، الودائع هي المصدر الرئيسي للتمويل، لذا نراقب إجمالي الالتزامات مقابل الحقوق."},
    'Real Estate': {'pe_limit': 22, 'de_limit': 1.1, 'payout': [70, 95], 'note': "🏠 ملاحظة: الريتات توزع 90%+ نظاماً، والديون طبيعية لتمويل العقارات."},
    'Default': {'pe_limit': 18, 'de_limit': 0.6, 'payout': [20, 75], 'note': "⚖️ ملاحظة: معايير قياسية صارمة لشركات الصناعة والتجزئة."}
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار التحكم الذكي</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (تداول):", "1150")
    scan_btn = st.button("تفعيل المسح العميق ⚡")

if scan_btn:
    with st.spinner("جاري تحليل الميزانية العمومية ومعالجة ديون البنوك..."):
        try:
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            bs = stock.balance_sheet # الميزانية
            divs = stock.dividends

            if 'currentPrice' in info or 'regularMarketPrice' in info:
                price = info.get('currentPrice') or info.get('regularMarketPrice', 1)
                sector = info.get('sector', 'Default')
                logic = SECTOR_DATA.get(sector, SECTOR_DATA['Default'])
                
                # --- محرك معالجة الديون (Fix for Banks) ---
                de_ratio = (info.get('debtToEquity', 0) or 0) / 100
                if de_ratio == 0 and sector == 'Financial Services':
                    # إذا كان بنكاً والديون 0، نقوم بحساب الرافعة المالية (إجمالي الالتزامات / الحقوق)
                    total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
                    total_equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 1
                    de_ratio = total_liab / total_equity if total_equity > 0 else 0

                # --- باقي الحسابات ---
                pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                real_divs = divs.last('365D').sum() if not divs.empty else 0
                r_yield = (real_divs / price) * 100

                score = 0
                rows_html = ""

                def add_row(name, result, criteria, is_pass):
                    global score
                    if is_pass: score += 1
                    s_class = "row-pass" if is_pass else "row-fail"
                    t_class = "pass-text" if is_pass else "fail-text"
                    icon = "✅" if is_pass else "❌"
                    return f"<tr class='{s_class}'><td><b>{name}</b></td><td class='{t_class}'>{icon} {result}</td><td>{criteria}</td></tr>"

                # تنفيذ المعايير الـ 7
                rows_html += add_row("مكرر الربحية (P/E)", f"{pe_val:.2f}", f"< {logic['pe_limit']}", 0 < pe_val <= logic['pe_limit'])
                rows_html += add_row("عائد التوزيع الحقيقي", f"{r_yield:.2f}%", "> 4%", r_yield >= 4.0)
                rows_html += add_row("نسبة التوزيع (Payout)", f"{payout:.1f}%", f"{logic['payout'][0]}-{logic['payout'][1]}%", logic['payout'][0] <= payout <= logic['payout'][1])
                rows_html += add_row("كفاءة الإدارة (ROE)", f"{roe:.1f}%", "> 15%", roe >= 15)
                rows_html += add_row("نسبة المديونية (D/E)", f"{de_ratio:.2f}", f"< {logic['de_limit']}", de_ratio <= logic['de_limit'])
                rows_html += add_row("سجل التوزيع", f"{len(divs.groupby(divs.index.year).sum())} سنة", "> 10 سنوات", len(divs.groupby(divs.index.year).sum()) >= 10)
                rows_html += add_row("السيولة (Current Ratio)", f"{info.get('currentRatio', 1.5):.2f}", "> 1.2", info.get('currentRatio', 1.5) >= 1.2)

                # العرض النهائي
                st.subheader(f"💎 تحليل: {info.get('longName', symbol)}")
                st.info(logic['note'])

                s_text = "🏆 سهم أرستقراطي ذهبي" if score >= 6 else "🟡 سهم عوائد جيد" if score >= 4 else "🔴 فخ عائد"
                s_color = "#00ff41" if score >= 6 else "#bb86fc" if score >= 4 else "#ff003c"
                st.markdown(f"<div class='status-box' style='color:{s_color};'>{s_text} ({score}/7)</div>", unsafe_allow_html=True)
                
                st.markdown(f"<table class='styled-table'><thead><tr><th>المؤشر المالي</th><th>النتيجة الفعلية</th><th>المعيار المطلوب</th></tr></thead><tbody>{rows_html}</tbody></table>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")
