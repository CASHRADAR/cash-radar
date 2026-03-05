import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Purple Neon)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #f0f0f0; }
    h1 { color: #e1bee7; text-shadow: 0 0 20px rgba(171, 71, 188, 0.6); text-align: center; }
    .status-box { padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0; font-size: 1.5em; border: 2px solid #9c27b0; }
    table { width: 100%; direction: rtl; border-collapse: collapse; background: rgba(255,255,255,0.02); }
    th { background: #4a148c; color: #e1bee7; padding: 15px; text-align: right; }
    td { padding: 12px; border-bottom: 1px solid #333; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color: #ba68c8;'>📊 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح البنفسجي ⚡")

if scan_btn:
    with st.spinner("جاري فحص القوائم المالية وتدقيق العوائد..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        
        # جلب البيانات مع معالجة الأخطاء
        try:
            info = stock.info
            fin = stock.financials
            divs = stock.dividends
            cash_flow = stock.cashflow
            
            if fin.empty or 'regularMarketPrice' not in info:
                st.error("❌ فشل جلب البيانات. تأكد من الرمز أو حاول لاحقاً.")
            else:
                price = info.get('regularMarketPrice', 1)
                score = 0
                analysis_data = []

                # --- 1. حساب العائد الحقيقي (آخر 12 شهر) ---
                real_div_amount = divs.last('365D').sum() if not divs.empty else 0
                real_yield = (real_div_amount / price) * 100 if price > 0 else 0

                # --- 2. مكرر الربحية التشغيلي ---
                op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
                shares = info.get('sharesOutstanding', 1)
                pe_op = price / (op_inc / shares) if op_inc > 0 else 0

                # --- دالة إضافة النتائج للجدول ---
                def add_metric(status_icon, name, result, desc, is_pass):
                    global score
                    if is_pass: score += 1
                    analysis_data.append([status_icon, name, result, desc])

                # تنفيذ المعايير
                # 1. سنوات التوزيع
                y_divs = divs.groupby(divs.index.year).sum() if not divs.empty else []
                div_yrs = len(y_divs)
                add_metric("✅" if div_yrs >= 10 else "❌", "استمرارية التوزيعات", f"{div_yrs} سنة", "بافيت: التاريخ الطويل يثبت استدامة التدفقات النقدية.", div_yrs >= 10)

                # 2. مكرر الربحية
                add_metric("✅" if 0 < pe_op <= 20 else "❌", "المكرر التشغيلي", f"{pe_op:.2f}", "جراهام: نشتري الأرباح التشغيلية الحقيقية لا الورقية.", 0 < pe_op <= 20)

                # 3. العائد الحقيقي
                add_metric("✅" if real_yield >= 4 else "❌", "عائد التوزيع", f"{real_yield:.2f}%", "المعيار: عائد فوق 4% يعتبر مجزياً للمستثمر.", real_yield >= 4)

                # 4. نسبة التوزيع
                payout = (info.get('payoutRatio', 0) or 0) * 100
                payout = payout / 100 if payout > 100 else payout
                add_metric("✅" if 20 <= payout <= 75 else "❌", "نسبة التوزيع (Payout)", f"{payout:.1f}%", "الأمان: النسبة المعتدلة تضمن استقرار التوزيع.", 20 <= payout <= 75)

                # 5. السيولة
                cr = info.get('currentRatio', 0) or 0
                add_metric("✅" if cr >= 1.5 else "❌", "السيولة (Current)", f"{cr:.2f}", "الأمان: قدرة الشركة على سداد التزاماتها القصيرة.", cr >= 1.5)

                # 6. الديون
                de = (info.get('debtToEquity', 0) or 0) / 100
                add_metric("✅" if de <= 0.6 else "❌", "الديون (D/E)", f"{de:.2f}", "الملاءة: الديون المنخفضة تقلل من مخاطر الفائدة.", de <= 0.6)

                # 7. كفاءة الإدارة
                roe = (info.get('returnOnEquity', 0) or 0) * 100
                add_metric("✅" if roe >= 15 else "❌", "كفاءة الإدارة (ROE)", f"{roe:.1f}%", "بافيت: قدرة الإدارة على توليد ربح من أموال المساهمين.", roe >= 15)

                # --- عرض النتائج ---
                st.write(f"### 💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
                
                if score >= 6: st.markdown("<div class='status-box' style='color:#00c853;'>🏆 التصنيف: سهم أرستقراطي ذهبي</div>", unsafe_allow_html=True); st.balloons()
                elif score >= 4: st.markdown("<div class='status-box' style='color:#ba68c8;'>🟡 التصنيف: سهم عوائد جيد</div>", unsafe_allow_html=True)
                else: st.markdown("<div class='status-box' style='color:#e74c3c;'>🔴 التصنيف: فخ عائد (Yield Trap)</div>", unsafe_allow_html=True)

                df = pd.DataFrame(analysis_data, columns=["حالة", "المؤشر", "النتيجة", "الشرح"])
                st.table(df)

        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء التحليل: {e}")

st.markdown("<p style='text-align: center; color: #444; font-size: 0.8em;'>تطوير: كاش رادار - الدقة المالية</p>", unsafe_allow_html=True)
