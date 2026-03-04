import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="كاش رادار | Cash Radar", page_icon="📡")

# تنسيق الواجهة
st.markdown("<h1 style='text-align: center; color: #00c853;'>📡 كاش رادار</h1>", unsafe_allow_html=True)
st.write("---")

symbol = st.text_input("أدخل رمز السهم (4 أرقام):", "2222")

if st.button("بدء المسح الراداري 🚀"):
    with st.spinner("جاري جلب أدق البيانات المالية..."):
        ticker_sym = f"{symbol}.SR"
        stock = yf.Ticker(ticker_sym)
        
        # جلب البيانات الأساسية
        info = stock.info
        # جلب تاريخ التوزيعات الفعلي (هنا السر في الدقة)
        dividends = stock.dividends
        
        if 'regularMarketPrice' in info:
            price = info.get('regularMarketPrice', 1)
            pe = info.get('trailingPE', 0)
            
            # حساب العائد يدوياً لآخر 12 شهر لضمان الدقة
            if not dividends.empty:
                last_year_divs = dividends.last('365D').sum()
                div_yield = last_year_divs / price
            else:
                div_yield = info.get('dividendYield', 0)
            
            payout = info.get('payoutRatio', 0)

            # عرض النتائج
            st.subheader(f"📊 نتائج شركة: {info.get('longName', symbol)}")
            c1, c2, c3 = st.columns(3)
            c1.metric("السعر الحالي", f"{price} ر.س")
            c2.metric("مكرر الربحية", f"{pe:.2f}" if pe else "N/A")
            c3.metric("عائد التوزيع الفعلي", f"{div_yield*100:.2f}%")

            # التقييم
            score = 0
            if 0 < pe <= 20: score += 1
            if div_yield >= 0.04: score += 1
            if 0.2 <= payout <= 0.75: score += 1
            
            st.write("---")
            if score >= 2:
                st.success(f"🎯 التقييم: {score}/3 - سهم ذهبي وفق الرادار")
            else:
                st.warning(f"⚠️ التقييم: {score}/3 - السهم يحتاج مراجعة")
        else:
            st.error("الرمز غير صحيح، يرجى المحاولة مرة أخرى.")
