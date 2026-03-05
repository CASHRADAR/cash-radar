import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="كاش رادار: نسخة التدقيق التشغيلي", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00c853;'>📡 كاش رادار: نسخة التدقيق التشغيلي</h1>", unsafe_allow_html=True)

# قاموس الديون الآمنة حسب القطاع (Debt/Equity)
SECTOR_DEBT_LIMITS = {
    'Energy': 0.80, 'Utilities': 1.20, 'Real Estate': 1.00,
    'Materials': 0.60, 'Industrials': 0.50, 'Consumer Defensive': 0.50,
    'Financial Services': 2.00, 'Technology': 0.40, 'Default': 0.50
}

symbol = st.sidebar.text_input("🔍 رمز السهم (مثال: 2222):", "2222")

if st.sidebar.button("تشغيل المسح الاحترافي 🚀"):
    with st.spinner("جاري تنقية الأرباح والتوزيعات من البنود الاستثنائية..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        financials = stock.financials # قائمة الدخل
        divs = stock.dividends
        
        if not financials.empty and 'regularMarketPrice' in info:
            score = 0
            results = []
            sector = info.get('sector', 'Default')
            debt_limit = SECTOR_DEBT_LIMITS.get(sector, SECTOR_DEBT_LIMITS['Default'])

            # 1. حساب مكرر الربحية التشغيلي (استبعاد الأرباح غير المتكررة)
            # Operating Income vs Net Income
            op_income = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else 0
            net_income = financials.loc['Net Income'].iloc[0] if 'Net Income' in financials.index else 1
            price = info.get('regularMarketPrice', 1)
            eps = info.get('trailingEps', 1)
            
            # إذا كان صافي الربح أكبر بكثير من التشغيلي، فهناك أرباح استثنائية
            is_extraordinary = net_income > (op_income * 1.2)
            pe_op = price / (op_income / info.get('sharesOutstanding', 1)) if op_income > 0 else 0
            
            if 0 < pe_op <= 20:
                score += 1
                results.append(f"✅ **مكرر الربحية التشغيلي:** عادل ({pe_op:.2f}). (تم استبعاد الأرباح الاستثنائية: {'نعم' if is_extraordinary else 'لا'})")
            else:
                results.append(f"❌ **مكرر الربحية التشغيلي:** مرتفع أو غير مستقر ({pe_op:.2f}).")

            # 2. تنقية التوزيعات (استبعاد التوزيعات الاستثنائية)
            if not divs.empty:
                # استبعاد القيم التي تزيد عن متوسط التوزيع بـ 3 أضعاف (كاستثناء)
                avg_div = divs.tail(8).mean() 
                clean_divs = divs[divs <= (avg_div * 2.5)].last('365D').sum()
                clean_yield = clean_divs / price
                if clean_yield >= 0.04:
                    score += 1
                    results.append(f"✅ **عائد التوزيع المستدام:** مجزي ({clean_yield*100:.1f}%). (مستبعد منها التوزيعات الخاصة)")
                else:
                    results.append(f"❌ **عائد التوزيع المستدام:** منخفض ({clean_yield*100:.1f}%).")

            # 3. نسبة الديون حسب القطاع
            de_ratio = info.get('debtToEquity', 0) / 100
            if de_ratio <= debt_limit:
                score += 1
                results.append(f"✅ **نسبة الديون (D/E):** آمنة لهذا القطاع ({de_ratio:.2f}). (الحد الأقصى لقطاع {sector}: {debt_limit})")
            else:
                results.append(f"❌ **نسبة الديون (D/E):** مرتفعة لقطاع {sector} ({de_ratio:.2f}).")

            # عرض التقرير النهائي
            st.header(f"تقرير التدقيق الاحترافي لـ {info.get('longName', symbol)}")
            st.write(f"**القطاع المستهدف:** {sector}")
            st.write("---")
            
            if score >= 2:
                st.success(f"🏆 النتيجة النهائية: {score}/3 | السهم اجتاز فلاتر الأرباح الحقيقية.")
            else:
                st.error(f"🔴 النتيجة النهائية: {score}/3 | تنبيه: السهم يعتمد على بنود استثنائية أو ديونه مقلقة.")

            for r in results:
                st.write(r)
        else:
            st.error("❌ تعذر جلب البيانات. يرجى التأكد من الرمز.")
