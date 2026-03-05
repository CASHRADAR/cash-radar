import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات المنصة الفخمة
st.set_page_config(page_title="CASH RADAR PRO", page_icon="📡", layout="wide")

# 2. تصميم الواجهة (Luxury Purple Neon)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #f0f0f0; }
    .metric-card { background: rgba(123, 31, 162, 0.05); border: 1px solid rgba(186, 104, 200, 0.3); border-radius: 15px; padding: 15px; text-align: center; }
    h1 { color: #e1bee7; text-shadow: 0 0 20px rgba(171, 71, 188, 0.6); text-align: center; font-family: 'Segoe UI'; }
    .analysis-row { background: rgba(255,255,255,0.03); padding: 15px; border-right: 4px solid #9c27b0; margin-bottom: 8px; border-radius: 5px; font-size: 0.95em; }
    .section-head { color: #ba68c8; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>📡 CASH RADAR PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>نظام التدقيق المالي المتطور | فكر بافيت، جراهام، ولينش</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color: #ba68c8;'>📊 رادار التحكم</h3>", unsafe_allow_html=True)
    symbol = st.text_input("كود السهم (تداول):", "2222")
    scan_btn = st.button("تفعيل المسح البنفسجي ⚡")

if scan_btn:
    with st.spinner("جاري فحص القوائم المالية لآخر 10 سنوات وتدقيق جودة الأرباح..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        fin = stock.financials # قائمة الدخل
        bs = stock.balance_sheet # الميزانية
        cf = stock.cashflow # التدفقات النقدية
        divs = stock.dividends
        
        if not fin.empty and not bs.empty:
            score = 0
            results = []
            price = info.get('regularMarketPrice', 1)
            shares = info.get('sharesOutstanding', 1)

            # --- [المحور الأول: الأمان والاستمرارية - الماضي] ---
            # 1. سجل التوزيعات (10 سنوات)
            y_divs = divs.groupby(divs.index.year).sum()
            div_yrs = len(y_divs)
            res = f"مؤشر استمرارية التوزيع: {div_yrs} سنة."
            if div_yrs >= 10: score += 1; results.append(f"✅ {res} (فلسفة جراهام: التاريخ الطويل يثبت صمود الشركة أمام الأزمات)")
            else: results.append(f"❌ {res} (تنبيه: السجل القصير لا يضمن استمرارية الدخل مستقبلاً)")

            # 2. نمو التوزيعات (5 سنوات)
            if div_yrs >= 5:
                growth = (y_divs.iloc[-1] / y_divs.iloc[-5]) - 1 if y_divs.iloc[-5] != 0 else 0
                if growth > 0: score += 1; results.append(f"✅ مؤشر نمو التوزيعات: +{growth*100:.1f}%. (فلسفة لينش: النمو السنوي يحمي محفظتك من التضخم)")
                else: results.append("❌ مؤشر نمو التوزيعات: ثابت أو متراجع. (تنبيه: قد يكون السهم في مرحلة تشبع أو تعثر)")

            # 3. سجل الأرباح (صافي ربح موجب)
            net_inc_hist = fin.loc['Net Income'].dropna() if 'Net Income' in fin.index else []
            pos_yrs = (pd.Series(net_inc_hist) > 0).sum()
            if pos_yrs >= 3: # ياهو يوفر 4 سنوات عادة، لذا نفحص الأغلبية
                score += 1; results.append(f"✅ سجل الربحية التاريخي: أرباح مستمرة. (فلسفة بافيت: نشتري الأعمال التي تدر مالاً حقيقياً لا وعوداً)")
            else: results.append("❌ سجل الربحية التاريخي: متذبذب. (تحذير: الشركة تعاني من تقلبات حادة في نتائجها)")

            # --- [المحور الثاني: الملاءة والتدقيق التشغيلي - الحاضر] ---
            # 4. نسبة التوزيع (Payout Ratio) - حساب يدوي لضمان الدقة
            payout = info.get('payoutRatio', 0)
            if payout > 1: payout = payout / 100
            res = f"مؤشر نسبة التوزيع (Payout): {payout*100:.1f}%."
            if 0.2 <= payout <= 0.7: score += 1; results.append(f"✅ {res} (المعيار: توزيع متزن يحافظ على كاش الشركة للتوسعات المستقبيلة)")
            else: results.append(f"❌ {res} (تحذير: نسبة مرتفعة جداً قد تؤدي لقطع التوزيع، أو منخفضة جداً تعني بخل الإدارة)")

            # 5. السيولة الجارية (Current Ratio)
            cr = info.get('currentRatio', 0)
            if cr >= 1.5: score += 1; results.append(f"✅ مؤشر السيولة (Current Ratio): {cr:.2f}. (المعيار: الشركة قادرة على سداد ديونها القصيرة بسهولة)")
            else: results.append(f"❌ مؤشر السيولة (Current Ratio): {cr:.2f}. (تنبيه: ضغوط سيولة قد تعيق العمليات التشغيلية)")

            # 6. نسبة الديون (D/E) حسب القطاع
            de = (info.get('debtToEquity', 0) or 0) / 100
            limit = 0.8 if info.get('sector') in ['Utilities', 'Energy'] else 0.5
            res = f"مؤشر الديون (D/E Ratio): {de:.2f}."
            if de <= limit: score += 1; results.append(f"✅ {res} (المعيار: هيكل رأس مال آمن يقلل من مخاطر الإفلاس أو تقلبات الفائدة)")
            else: results.append(f"❌ {res} (تحذير: ديون مرتفعة تستهلك الأرباح في خدمة الدين)")

            # 7. التدفق النقدي الحر (Free Cash Flow)
            fcf = cf.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cf.index else 0
            if fcf > 0: score += 1; results.append("✅ مؤشر التدفق النقدي (FCF): إيجابي. (فلسفة بافيت: الكاش هو الملك، وهو المصدر الحقيقي للتوزيعات)")
            else: results.append("❌ مؤشر التدفق النقدي (FCF): سلبي. (تحذير: الشركة تنفق أكثر مما تجني، التوزيعات قد تكون من ديون)")

            # --- [المحور الثالث: الجودة والسعر العادل - المستقبل] ---
            # 8. مكرر الربحية التشغيلي (استبعاد الاستثنائي)
            op_inc = fin.loc['Operating Income'].iloc[0] if 'Operating Income' in fin.index else 0
            pe_op = price / (op_inc / shares) if op_inc > 0 else 0
            res = f"مؤشر المكرر التشغيلي: {pe_op:.2f}."
            if 0 < pe_op <= 20: score += 1; results.append(f"✅ {res} (فلسفة جراهام: شراء السهم بسعر عادل مقارنة بربحه التشغيلي الحقيقي)")
            else: results.append(f"❌ {res} (تنبيه: السعر متضخم مقارنة بالأداء الفعلي)")

            # 9. كفاءة الإدارة (ROE)
            roe = (info.get('returnOnEquity', 0) or 0) * 100
            if roe >= 15: score += 1; results.append(f"✅ مؤشر كفاءة الإدارة (ROE): {roe:.1f}%. (المعيار: الإدارة تحقق عائداً ممتازاً على أموال المساهمين)")
            else: results.append(f"❌ مؤشر كفاءة الإدارة (ROE): {roe:.1f}%. (تنبيه: كفاءة تدوير رأس المال دون المأمول)")

            # 10. نمو الأرباح المتوقع
            eg = (info.get('earningsQuarterlyGrowth', 0) or 0) * 100
            if eg >= 5: score += 1; results.append(f"✅ مؤشر نمو الأرباح: +{eg:.1f}%. (المعيار: استمرار النمو يضمن زيادة قيمة السهم مستقبلاً)")
            else: results.append(f"❌ مؤشر نمو الأرباح: ضعيف. (تنبيه: الشركة قد تكون في مرحلة ركود)")

            # --- [العرض النهائي الفخم] ---
            st.write("### 💎 نتائج التدقيق المالي الشامل")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("السعر الحالي", f"{price} ر.س")
            c2.metric("عائد التوزيع", f"{info.get('dividendYield',0)*100:.2f}%")
            c3.metric("مكرر الربحية", f"{pe_op:.1f}")
            c4.metric("مجموع النقاط", f"{score}/10")

            st.write("---")
            if score >= 8: st.success("🏆 التصنيف: سهم أرستقراطي ذهبي - نخبة أسهم العوائد"); st.balloons()
            elif score >= 5: st.warning("🟡 التصنيف: سهم عوائد جيد - يحتاج لمتابعة ربعية")
            else: st.error("🔴 التصنيف: فخ عائد (Yield Trap) - مخاطرة عالية جداً")

            st.write("### 📝 التقرير التحليلي المفصل:")
            for r in results:
                st.markdown(f"<div class='analysis-row'>{r}</div>", unsafe_allow_html=True)
        else: st.error("❌ عذراً، القوائم المالية لهذا السهم غير مكتملة في ياهو فاينانس حالياً.")

st.markdown("<br><p style='text-align: center; color: #444; font-size: 0.8em;'>حقوق الملكية الفكرية: كاش رادار - الجيل الذكي</p>", unsafe_allow_html=True)

