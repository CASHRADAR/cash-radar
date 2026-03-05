import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة العصرية (Modern Dark UI)
st.markdown("""
    <style>
    /* تحسين لون الخلفية والنص لتباين عالٍ */
    .stApp { background-color: #0d0d12; color: #ffffff; }
    h1 { color: #bb86fc; text-shadow: 0 0 15px rgba(187, 134, 252, 0.5); text-align: center; font-family: 'Inter', sans-serif; font-weight: 800; margin-bottom: 40px; }
    
    /* تصميم بطاقات النتائج (Modern Cards) */
    .result-card {
        background: #1a1a24;
        border-right: 5px solid #bb86fc;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-name { color: #bb86fc; font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
    .metric-value { color: #ffffff; font-size: 1.3em; font-weight: 700; margin-left: 10px; }
    .metric-desc { color: #a0a0a0; font-size: 0.95em; line-height: 1.6; margin-top: 8px; }
    
    /* صندوق الحالة النهائية */
    .status-box {
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.8em;
        font-weight: 800;
        margin: 30px 0;
        background: #16161e;
        border: 2px solid #3700b3;
    }
    
    /* تحسين مظهر الجانب الأيسر */
    .stSidebar { background-color: #16161e !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>")

with st.sidebar:
    st.markdown("<h3 style='color: #bb86fc;'>📊 لوحة التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (تداول):", "2222")
    scan_btn = st.button("تشغيل المسح الذكي ✨")
    st.write("---")
    st.markdown("<p style='color: #888; font-size: 0.8em;'>تم بناء المعايير وفق دراسات: بافيت، جراهام، ولينش.</p>", unsafe_allow_html=True)

if scan_btn:
    with st.spinner("جاري تحليل البيانات المالية وتدقيق العوائد..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        
        try:
            info = stock.info
            fin = stock.financials
            divs = stock.dividends
            
            if fin.empty or 'regularMarketPrice' not in info:
                st.error("❌ تعذر جلب البيانات. تأكد من الرمز (مثل 2222 للسوق السعودي).")
            else:
                price = info.get('regularMarketPrice', 1)
                score = 0
                
                # --- محرك الحسابات الدقيقة ---
                # 1. العائد الحقيقي
                real_div_amount = divs.last('365D').sum() if not divs.empty else 0
                real_yield = (real_div_amount / price) * 100 if price > 0 else 0
                
                # 2. مكرر الربحية التشغيلي
                op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
                shares = info.get('sharesOutstanding', 1)
                pe_op = price / (op_inc / shares) if op_inc > 0 else 0

                # دالة لعرض البطاقة العصرية
                def display_card(icon, name, value, desc, is_pass):
                    global score
                    if is_pass: score += 1
                    border_color = "#03dac6" if is_pass else "#cf6679" # أخضر مائي للنجاح، أحمر مرجاني للفشل
                    st.markdown(f"""
                        <div class="result-card" style="border-right-color: {border_color};">
                            <div class="metric-name">{icon} {name}</div>
                            <div class="metric-value">النتيجة: {value}</div>
                            <div class="metric-desc"><b>الفلسفة الاستثمارية:</b> {desc}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # --- عرض التقييم النهائي أولاً لإبهار المستخدم ---
                st.subheader(f"💎 تحليل شركة: {info.get('longName', symbol)}")
                
                # (سيتم حساب النقاط أولاً في الخلفية ثم عرض الصندوق)
                # ملاحظة: برمجياً سنقوم بتنفيذ المعايير ثم استخدام st.empty لوضع الحالة في الأعلى
                status_placeholder = st.empty()

                # --- تنفيذ معايير الرادار ---
                y_divs = divs.groupby(divs.index.year).sum() if not divs.empty else []
                div_yrs = len(y_divs)
                
                display_card("📅", "استمرارية التوزيعات", f"{div_yrs} سنة", "بنجامين جراهام: التاريخ الطويل (أكثر من 10 سنوات) يثبت أن الشركة تملك أساساً مالياً صلباً قادراً على الصمود في الأزمات.", div_yrs >= 10)
                
                display_card("📈", "المكرر التشغيلي (P/E)", f"{pe_op:.2f}", "جراهام: نبحث عن شراء الأرباح الناتجة عن النشاط الأساسي بسعر عادل (أقل من 20) لتجنب الفقاعات السعرية.", 0 < pe_op <= 20)
                
                display_card("💰", "عائد التوزيع الحقيقي", f"{real_yield:.2f}%", "المعيار: عائد فوق 4% يعتبر مجزياً للمستثمر، وهو المصدر الحقيقي للدخل السلبي المتنامي.", real_yield >= 4)
                
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                display_card("⚖️", "نسبة التوزيع (Payout Ratio)", f"{payout:.1f}%", "الأمان: النسبة المعتدلة (20-70%) تضمن قدرة الشركة على دفع الأرباح حتى في سنوات الركود.", 20 <= payout <= 70)
                
                cr = info.get('currentRatio', 0) or 0
                display_card("🛡️", "نسبة السيولة (Current Ratio)", f"{cr:.2f}", "الملاءة: قدرة الشركة على سداد التزاماتها قصيرة الأجل دون الحاجة للاقتراض أو بيع الأصول.", cr >= 1.5)
                
                de = (info.get('debtToEquity', 0) or 0) / 100
                display_card("📉", "نسبة الديون (D/E Ratio)", f"{de:.2f}", "المخاطر: الديون المنخفضة (أقل من 0.6) تقلل من ضغوط الفوائد البنكية وتؤمن حقوق المساهمين.", de <= 0.6)
                
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                display_card("🚀", "كفاءة الإدارة (ROE)", f"{roe:.1f}%", "وارن بافيت: أهم مقياس لقدرة الإدارة على توليد أرباح استثنائية من كل ريال يستثمره المساهمون.", roe >= 15)

                # تحديث صندوق الحالة النهائية بناءً على المجموع
                if score >= 6:
                    status_placeholder.markdown(f"<div class='status-box' style='color:#03dac6;'>🏆 التصنيف: سهم أرستقراطي ذهبي ({score}/7)</div>", unsafe_allow_html=True)
                    st.balloons()
                elif score >= 4:
                    status_placeholder.markdown(f"<div class='status-box' style='color:#bb86fc;'>🟡 التصنيف: سهم عوائد جيد ({score}/7)</div>", unsafe_allow_html=True)
                else:
                    status_placeholder.markdown(f"<div class='status-box' style='color:#cf6679;'>🔴 التصنيف: فخ عائد - مخاطرة عالية ({score}/7)</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"⚠️ حدث خطأ تقني: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em; margin-top: 50px;'>CASH RADAR - NEXT GEN FINANCIAL ANALYSIS</p>", unsafe_allow_html=True)
