import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="كاش رادار | Cash Radar PRO", layout="wide")

# تصميم الهوية البصرية
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    h1, h2, h3 { color: #00c853; text-align: center; }
    . aristocratic { color: #d4af37; font-weight: bold; font-size: 1.5em; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 كاش رادار: نسخة النخبة الاستثمارية")
st.write("---")

symbol = st.sidebar.text_input("🔍 أدخل رمز السهم (مثال: 2222):", "2222")

if st.sidebar.button("تشغيل المسح الشامل 🚀"):
    with st.spinner("جاري جلب البيانات المالية التاريخية وتحليل المحاور الثلاثة..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        
        # جلب البيانات
        info = stock.info
        hist_divs = stock.dividends
        financials = stock.financials # قائمة الدخل
        balance_sheet = stock.balance_sheet # الميزانية
        cashflow = stock.cashflow # التدفقات النقدية
        
        if not financials.empty and 'regularMarketPrice' in info:
            price = info.get('regularMarketPrice', 0)
            score = 0
            analysis = []

            # --- المحور الأول: الأمان والاستمرارية (الماضي) ---
            # 1. سجل التوزيعات (10 سنوات)
            div_years = len(hist_divs.groupby(hist_divs.index.year).sum())
            if div_years >= 10:
                score += 1
                analysis.append("✅ سجل توزيعات طويل (أكثر من 10 سنوات)")
            else: analysis.append("❌ سجل توزيعات قصير")

            # 2. نمو التوزيعات (5 سنوات)
            div_growth = hist_divs.groupby(hist_divs.index.year).sum().tail(5).pct_change().dropna()
            if not div_growth.empty and (div_growth > 0).all():
                score += 1
                analysis.append("✅ نمو مستمر في التوزيعات لآخر 5 سنوات")
            else: analysis.append("❌ لا يوجد نمو مستمر في التوزيعات")

            # 3. سجل الأرباح (صافي ربح موجب)
            net_income = financials.loc['Net Income'].tail(10) if 'Net Income' in financials.index else pd.Series()
            if (net_income > 0).sum() >= 9:
                score += 1
                analysis.append("✅ سجل أرباح نظيف (ربحية في 9 من أصل 10 سنوات)")
            else: analysis.append("❌ سجل أرباح متذبذب")

            # --- المحور الثاني: الملاءة والقدرة (الحاضر) ---
            # 4. نسبة التوزيع (20-60%)
            payout = info.get('payoutRatio', 0)
            if 0.2 <= payout <= 0.6:
                score += 1
                analysis.append(f"✅ نسبة توزيع آمنة ومستدامة ({payout*100:.1f}%)")
            else: analysis.append(f"❌ نسبة التوزيع غير مثالية ({payout*100:.1f}%)")

            # 5. نسبة السيولة (Current Ratio > 2)
            current_ratio = info.get('currentRatio', 0)
            if current_ratio >= 2:
                score += 1
                analysis.append(f"✅ سيولة قوية: النسبة الجارية {current_ratio:.2f}")
            else: analysis.append(f"❌ سيولة ضعيفة: النسبة الجارية {current_ratio:.2f}")

            # 6. نسبة الديون (Debt/Equity < 0.5)
            de_ratio = info.get('debtToEquity', 0) / 100
            if 0 < de_ratio <= 0.5:
                score += 1
                analysis.append(f"✅ ديون منخفضة وآمنة ({de_ratio:.2f})")
            else: analysis.append(f"❌ ديون مرتفعة نسبياً ({de_ratio:.2f})")

            # 7. التدفق النقدي الحر (FCF > Dividends)
            fcf = cashflow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cashflow.index else 0
            total_div_paid = abs(cashflow.loc['Cash Dividends Paid'].iloc[0]) if 'Cash Dividends Paid' in cashflow.index else 0
            if fcf > total_div_paid:
                score += 1
                analysis.append("✅ التدفق النقدي يغطي التوزيعات بزيادة")
            else: analysis.append("❌ التوزيعات تضغط على السيولة النقدية")

            # --- المحور الثالث: الجودة والسعر العادل (المستقبل) ---
            # 8. العائد على حقوق المساهمين (ROE > 15%)
            roe = info.get('returnOnEquity', 0)
            if roe >= 0.15:
                score += 1
                analysis.append(f"✅ كفاءة إدارة عالية: ROE {roe*100:.1f}%")
            else: analysis.append(f"❌ ROE أقل من المستهدف ({roe*100:.1f}%)")

            # 9. مكرر الربحية (P/E < 20)
            pe = info.get('trailingPE', 0)
            if 0 < pe <= 20:
                score += 1
                analysis.append(f"✅ سعر عادل: مكرر الربحية {pe:.2f}")
            else: analysis.append(f"❌ سعر متضخم: مكرر الربحية {pe:.2f}")

            # 10. نمو الأرباح (EPS Growth > 5%)
            eps_growth = info.get('earningsQuarterlyGrowth', 0)
            if eps_growth >= 0.05:
                score += 1
                analysis.append(f"✅ نمو أرباح جيد ({eps_growth*100:.1f}%)")
            else: analysis.append(f"❌ نمو أرباح ضعيف ({eps_growth*100:.1f}%)")

            # --- عرض النتائج النهائية ---
            st.header(f"نتائج رادار النخبة: {info.get('longName', symbol)}")
            
            # عرض التقييم النهائي
            st.write("---")
            if score >= 8:
                st.balloons()
                st.markdown(f"<p class='aristocratic'>🏆 التقييم النهائي: {score}/10 - سهم أرستقراطي ممتاز</p>", unsafe_allow_html=True)
            elif score >= 5:
                st.warning(f"🟡 التقييم النهائي: {score}/10 - سهم عوائد جيد (يحتاج مراقبة)")
            else:
                st.error(f"🔴 التقييم النهائي: {score}/10 - سهم خطر (فخ عائد)")

            # عرض تفاصيل المحاور
            with st.expander("تفاصيل الفحص لجميع المعايير"):
                for item in analysis:
                    st.write(item)
        else:
            st.error("لم يتم العثور على بيانات مالية كافية لهذا الرمز.")

st.info("ملاحظة: كاش رادار يقوم الآن بفحص الميزانية والتدفقات النقدية وقائمة الدخل لآخر 10 سنوات لإتمام التقييم.")
