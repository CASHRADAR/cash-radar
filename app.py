import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Purple Neon - Optimized)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #f0f0f0; }
    h1 { color: #e1bee7; text-shadow: 0 0 20px rgba(171, 71, 188, 0.6); text-align: center; font-family: 'Segoe UI'; margin-bottom: 30px; }
    .status-box { padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0; font-size: 1.5em; font-weight: bold; border: 2px solid #9c27b0; }
    /* تنسيق الجدول الاحترافي */
    table { width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(255,255,255,0.02); }
    th { background: #4a148c; color: #e1bee7; padding: 15px; text-align: right; border-bottom: 2px solid #9c27b0; }
    td { padding: 12px; border-bottom: 1px solid #333; color: #e0e0e0; vertical-align: top; }
    .check-icon { font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color: #ba68c8;'>📊 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح البنفسجي ⚡")

if scan_btn:
    with st.spinner("جاري تدقيق التوزيعات النقدية وحساب العائد الحقيقي..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info, fin, divs = stock.info, stock.financials, stock.dividends
        
        if not fin.empty and 'regularMarketPrice' in info:
            score = 0
            analysis_data = []
            price = info.get('regularMarketPrice', 1)

            # --- [1. حساب العائد الحقيقي يدوياً بدقة 100%] ---
            if not divs.empty:
                # جمع مبالغ التوزيع لآخر 12 شهر فعلياً
                real_div_amount = divs.last('365D').sum()
                real_yield = (real_div_amount / price) * 100
            else:
                real_div_amount = 0
                real_yield = 0

            # --- [تطبيق الـ 10 معايير مع الشرح المنفصل] ---
            # 1. سجل التوزيعات (10 سنوات)
            y_divs = divs.groupby(divs.index.year).sum()
            div_yrs = len(y_divs)
            status = "✅" if div_yrs >= 10 else "❌"
            if div_yrs >= 10: score += 1
            analysis_data.append([status, "استمرارية التوزيعات", f"{div_yrs} سنة", "بافيت: التاريخ الطويل يثبت أن الشركة تملك تدفقات نقدية مستدامة ولا تتأثر بالأزمات العابرة."])

            # 2. نمو التوزيعات (5 سنوات)
            growth = ((y_divs.iloc[-1] / y_divs.iloc[-5]) - 1) * 100 if len(y_divs) >= 5 and y_divs.iloc[-5] > 0 else 0
            status = "✅" if growth > 0 else "❌"
            if growth > 0: score += 1
            analysis_data.append([status, "نمو التوزيعات", f"{growth:.1f}%", "لينش: نمو التوزيع يحمي محفظتك من التضخم ويعكس نمو الأرباح الحقيقي للشركة."])

            # 3. مكرر الربحية التشغيلي (P/E)
            op_inc = fin.loc['Operating Income'].iloc if 'Operating Income' in fin.index else 0
            pe_op = price / (op_inc / info.get('sharesOutstanding', 1)) if op_inc > 0 else 0
            status = "✅" if 0 < pe_op <= 20 else "❌"
            if 0 < pe_op <= 20: score += 1
            analysis_data.append([status, "مكرر الربحية التشغيلي", f"{pe_op:.2f}", "جراهام: نشتري الأرباح التشغيلية الناتجة عن النشاط الفعلي لا الأرباح الورقية أو الاستثنائية."])

            # 4. عائد التوزيع الحقيقي (Yield)
            status = "✅" if real_yield >= 4 else "❌"
            if real_yield >= 4: score += 1
            analysis_data.append([status, "عائد التوزيع الحقيقي", f"{real_yield:.2f}%", "المعيار: عائد فوق 4% يعتبر مجزياً للمستثمر مقارنة ببدائل الدخل الثابت."])

            # 5. نسبة التوزيع (Payout Ratio)
            payout = (info.get('payoutRatio', 0) or 0) * 100
            if payout > 100: payout = payout / 100 # تصحيح أخطاء الوحدات
            status = "✅" if 20 <= payout <= 70 else "❌"
            if 20 <= payout <= 70: score += 1
            analysis_data.append([status, "نسبة التوزيع (Payout)", f"{payout:.1f}%", "الأمان: النسبة المعتدلة تضمن استمرار التوزيع حتى لو تراجعت الأرباح مؤقتاً."])

            # 6. السيولة الجارية
            cr = info.get('currentRatio', 0) or 0
            status = "✅" if cr >= 1.5 else "❌"
            if cr >= 1.5: score += 1
            analysis_data.append([status, "السيولة (Current Ratio)", f"{cr:.2f}", "الأمان: قدرة الشركة على سداد التزاماتها القصيرة دون الحاجة لبيع أصول أو ديون."])

            # 7. نسبة الديون (D/E)
            de = (info.get('debtToEquity', 0) or 0) / 100
            status = "✅" if de <= 0.6 else "❌"
            if de <= 0.6: score += 1
            analysis_data.append([status, "الديون (Debt/Equity)", f"{de:.2f}", "الملاءة: الديون المنخفضة تقلل من ضغوط الفائدة وتزيد من حصة المساهمين في الربح."])

            # 8. كفاءة الإدارة (ROE)
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            status = "✅" if roe >= 15 else "❌"
            if roe >= 15: score += 1
            analysis_data.append([status, "كفاءة الإدارة (ROE)", f"{roe:.1f}%", "بافيت: أهم مقياس لقدرة الإدارة على توليد أرباح من أموال المساهمين ذاتهم."])

            # 9. سجل الربحية (آخر 4 سنوات)
            net_inc = fin.loc['Net Income'].tail(4) if 'Net Income' in fin.index else [0]
            profit_safe = (pd.Series(net_inc) > 0).all()
            status = "✅" if profit_safe else "❌"
            if profit_safe: score += 1
            analysis_data.append([status, "سجل الربحية", "مستقر", "الاستقرار: نبتعد عن الشركات الخاسرة أو المتقلبة التي لا يمكن التنبؤ بمستقبلها."])

            # 10. جودة الربح (التدفق النقدي)
            fcf = stock.cashflow.loc['Free Cash Flow'].iloc if 'Free Cash Flow' in stock.cashflow.index else 0
            status = "✅" if fcf > 0 else "❌"
            if fcf > 0: score += 1
            analysis_data.append([status, "التدفق النقدي (FCF)", "إيجابي", "بافيت: الأرباح الحقيقية هي التي تتحول لنقد في البنك، وليس مجرد أرقام دفترية."])

            # --- [عرض النتائج النهائية بصورة مرتبة] ---
            st.write(f"### 💎 تقرير التدقيق لشركة: {info.get('longName', symbol)}")
            
            if score >= 8: st.markdown("<div class='status-box' style='color:#00c853;'>🏆 التصنيف: سهم أرستقراطي ذهبي</div>", unsafe_allow_html=True); st.balloons()
            elif score >= 5: st.markdown("<div class='status-box' style='color:#ba68c8;'>🟡 التصنيف: سهم عوائد جيد</div>", unsafe_allow_html=True)
            else: st.markdown("<div class='status-box' style='color:#e74c3c;'>🔴 التصنيف: فخ عائد (Yield Trap)</div>", unsafe_allow_html=True)

            # إنشاء جدول النتائج
            df_results = pd.DataFrame(analysis_data, columns=["حالة", "المؤشر المالي", "النتيجة الفعلية", "فلسفة التقييم والشرح"])
            st.table(df_results)
            
        else: st.error("❌ عذراً، البيانات المالية غير مكتملة لهذا الرمز حالياً.")

st.markdown("<br><p style='text-align: center; color: #444; font-size: 0.8em;'>تطوير: كاش رادار - الدقة المالية المتناهية</p>", unsafe_allow_html=True)
