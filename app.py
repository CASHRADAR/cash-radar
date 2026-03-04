import streamlit as st
import yfinance as yf
import pandas as pd

# 1. إعدادات الصفحة والهوية البصرية لـ "كاش رادار"
st.set_page_config(page_title="كاش رادار | Cash Radar", page_icon="📡", layout="centered")

# إضافة لمسة جمالية CSS (اختياري)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00c853; color: black; font-weight: bold; height: 3em; }
    h1 { color: #00c853; text-align: center; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .metric-box { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. العنوان والشعار
st.markdown("<h1>📡 كاش رادار | Cash Radar</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>الرادار الذكي لاصطياد أسهم العوائد الممتازة في السوق السعودي</p>", unsafe_allow_html=True)
st.write("---")

# 3. مدخلات المستخدم (رمز السهم)
symbol = st.text_input("أدخل رمز السهم (4 أرقام - مثال: 2222 لأرامكو):", value="2222")

if st.button("بدء المسح الراداري 🚀"):
    with st.spinner("جاري فحص رادار العوائد وتحليل البيانات..."):
        try:
            # جلب البيانات من ياهو فاينانس (إضافة .SR للسوق السعودي)
            ticker_sym = f"{symbol}.SR"
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            
            if 'regularMarketPrice' in info:
                # استخراج المؤشرات المالية الأساسية
                name = info.get('longName', 'شركة غير معروفة')
                price = info.get('regularMarketPrice', 0)
                pe = info.get('trailingPE', 0)
                payout = info.get('payoutRatio', 0)
                div_yield = info.get('dividendYield', 0)
                
                # عرض البيانات الأساسية في أعمدة
                st.subheader(f"📊 نتائج المسح لشركة: {name}")
                col1, col2, col3 = st.columns(3)
                col1.metric("السعر الحالي", f"{price} ر.س")
                col2.metric("مكرر الربحية (P/E)", f"{pe:.2f}" if pe else "N/A")
                col3.metric("عائد التوزيع", f"{div_yield*100:.2f}%" if div_yield else "0%")

                # 4. خوارزمية التقييم (معايير جراهام وبافيت)
                score = 0
                analysis_results = []
                
                # المعيار الأول: مكرر الربحية (P/E)
                if 0 < pe <= 20:
                    score += 1
                    analysis_results.append("✅ **السعر عادل:** مكرر الربحية ضمن النطاق الآمن (أقل من 20).")
                else:
                    analysis_results.append("❌ **تنبيه:** مكرر الربحية مرتفع أو الشركة خاسرة.")

                # المعيار الثاني: نسبة التوزيع (Payout Ratio)
                if 0.2 <= payout <= 0.7:
                    score += 1
                    analysis_results.append("✅ **استدامة:** نسبة توزيع الأرباح متزنة وتسمح بالنمو.")
                else:
                    analysis_results.append("❌ **تنبيه:** نسبة التوزيع غير مثالية (قد تكون مرتفعة جداً أو منخفضة جداً).")

                # المعيار الثالث: عائد التوزيع (Dividend Yield)
                if div_yield >= 0.04:
                    score += 1
                    analysis_results.append("✅ **عائد مجزي:** السهم يمنح عائداً نقدياً يتجاوز 4%.")
                else:
                    analysis_results.append("❌ **تنبيه:** عائد التوزيع السنوي منخفض حالياً.")

                # 5. عرض النتيجة النهائية للرادار
                st.write("---")
                if score >= 2:
                    st.success(f"🎯 **النتيجة النهائية: {score}/3** - السهم ضمن نطاق 'الرادار الذهبي' كفرصة عوائد.")
                else:
                    st.warning(f"⚠️ **النتيجة النهائية: {score}/3** - السهم خارج نطاق العوائد الممتازة وفق المعايير الحالية.")
                
                # عرض التفاصيل للمستخدم
                for res in analysis_results:
                    st.write(res)
            else:
                st.error("❌ لم يتم العثور على بيانات لهذا الرمز. تأكد من إدخال 4 أرقام صحيحة.")
        
        except Exception as e:
            st.error(f"عذراً، حدث خطأ أثناء جلب البيانات: {str(e)}")

# تذييل الصفحة
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8em; color: #8b949e;'>كاش رادار | تم التطوير باستخدام بيانات Yahoo Finance الحية</p>", unsafe_allow_html=True)