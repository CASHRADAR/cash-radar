import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة
st.set_page_config(page_title="CASH RADAR PRO | High Fidelity", layout="wide")

# 2. الواجهة البنفسجية المتطورة (Luxury Dark Theme)
st.markdown("""
    <style>
    .stApp { background-color: #0b0b10; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 20px rgba(187, 134, 252, 0.4); text-align: center; font-weight: 800; }
    .sector-note { background: rgba(187, 134, 252, 0.05); border-right: 5px solid #bb86fc; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 0.9em; line-height: 1.6; }
    .result-card { background: #161620; border-right: 5px solid #bb86fc; padding: 18px; margin-bottom: 12px; border-radius: 12px; border: 1px solid #252535; }
    .metric-name { color: #bb86fc; font-weight: bold; }
    .metric-value { color: #03dac6; font-size: 1.2em; font-weight: 700; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 1.7em; font-weight: 800; background: #1a1a2e; border: 2px solid #3700b3; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

# 3. مصفوفة "الالتزام بجوهر المحللين" (تعديل قطاع التقنية ليكون صارماً)
SECTOR_LOGIC = {
    'Technology': {
        'pe_limit': 25, 'de_limit': 0.4, 'payout': [20, 60], 'roe_min': 20,
        'note': "⚠️ **رؤية بافيت ولينش للتقنية:** لا ننجرف خلف المكررات الفلكية. اشترطنا مكرر أقصى 25 (لينش)، وديون منخفضة جداً أقل من 0.4، وعائد حقوق مساهمين مرتفع جداً (ROE > 20%) لضمان الجودة."
    },
    'Financial Services': {
        'pe_limit': 15, 'de_limit': 2.5, 'payout': [30, 70], 'roe_min': 15,
        'note': "💡 **قطاع مالي:** نعتمد مكرر جراهام الصارم (15). الديون هنا ودائع، لذا نركز على استقرار التوزيعات وكفاءة الإدارة."
    },
    'Real Estate': {
        'pe_limit': 22, 'de_limit': 1.0, 'payout': [70, 95], 'roe_min': 8,
        'note': "🏠 **قطاع عقاري (REIT):** نلتزم بنظام الـ 90% توزيع. الديون مقبولة لتمويل الأصول الثابتة التي تدر إيجارات."
    },
    'Utilities': {
        'pe_limit': 15, 'de_limit': 1.2, 'payout': [40, 85], 'roe_min': 10,
        'note': "⚡ **قطاع المرافق:** شركات دفاعية. نقبل ديون أعلى قليلاً لاستقرار الكاش، لكن بمكرر منخفض جداً (جراهام)."
    },
    'Default': {
        'pe_limit': 18, 'de_limit': 0.5, 'payout': [20, 70], 'roe_min': 15,
        'note': "⚖️ **المعايير القياسية:** الالتزام الحرفي بمدرسة الاستثمار القيمة (P/E < 18، ديون < 0.5)."
    }
}

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>🔍 رادار النخبة الاستثمارية</h3>", unsafe_allow_html=True)
    symbol = st.text_input("رمز السهم (مثال: 2222، 7202، 1150):", "2222")
    scan_btn = st.button("بدء المسح الراداري 🚀")

if scan_btn:
    with st.spinner("جاري تدقيق البيانات وفق معايير بافيت وجراهام..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        
        try:
            info = stock.info
            divs = stock.dividends
            price = info.get('regularMarketPrice', 1)
            sector = info.get('sector', 'Default')
            
            # جلب المنطق المخصص
            logic = SECTOR_LOGIC.get(sector, SECTOR_LOGIC['Default'])
            if 'REIT' in info.get('industry', ''): logic = SECTOR_LOGIC['Real Estate']

            # --- حسابات الدقة الحيوية ---
            pe_val = info.get('trailingPE') or (price / (info.get('trailingEps') or 1))
            de_ratio = (info.get('debtToEquity', 0) or 0) / 100
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            payout = (info.get('payoutRatio', 0) or 0) * 100
            if payout > 100: payout = payout / 100
            
            # العائد الحقيقي لآخر 365 يوم
            real_yield = (divs.last('365D').sum() / price) * 100 if not divs.empty else 0
            div_yrs = len(divs.groupby(divs.index.year).sum())

            st.subheader(f"💎 تحليل: {info.get('longName', symbol)}")
            st.markdown(f"<div class='sector-note'>{logic['note']}</div>", unsafe_allow_html=True)
            
            score = 0
            def display_card(icon, name, value, desc, is_pass):
                global score
                if is_pass: score += 1
                color = "#03dac6" if is_pass else "#cf6679"
                st.markdown(f"""
                    <div class="result-card" style="border-right-color: {color};">
                        <span class='metric-name'>{icon} {name}</span> | <span class='metric-value'>{value}</span><br>
                        <span style='color: #888; font-size: 0.85em;'>🎯 المعيار: {desc}</span>
                    </div>
                """, unsafe_allow_html=True)

            # --- تطبيق المعايير الصارمة ---
            display_card("📅", "استمرارية التوزيع", f"{div_yrs} سنة", "أكثر من 10 سنوات (جراهام).", div_yrs >= 10)
            display_card("📈", "مكرر الربحية (P/E)", f"{pe_val:.2f}", f"أقل من {logic['pe_limit']} (الانضباط السعري).", 0 < pe_val <= logic['pe_limit'])
            display_card("💰", "العائد الحقيقي", f"{real_yield:.2f}%", "عائد فوق 4% (المصدر الحقيقي للدخل).", real_yield >= 4.0)
            display_card("⚖️", "نسبة التوزيع (Payout)", f"{payout:.1f}%", f"بين {logic['payout'][0]}% و {logic['payout'][1]}% (الاستدامة).", logic['payout'][0] <= payout <= logic['payout'][1])
            display_card("📉", "نسبة الديون (D/E)", f"{de_ratio:.2f}", f"أقل من {logic['de_limit']} (الأمان المالي).", de_ratio <= logic['de_limit'])
            display_card("🚀", "كفاءة الإدارة (ROE)", f"{roe:.1f}%", f"فوق {logic['roe_min']}% (كفاءة توليد الأرباح).", roe >= logic['roe_min'])

            st.write("---")
            if score >= 5:
                st.markdown(f"<div class='status-box' style='color:#03dac6;'>🏆 سهم نخبة ذهبي ({score}/6)</div>", unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"<div class='status-box' style='color:#cf6679;'>🔴 سهم خارج النطاق ({score}/6)</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ خطأ في معالجة البيانات: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR PRO | 2026 EDITION</p>", unsafe_allow_html=True)
