import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="بوابة الرواتب | جامعة ابن سينا", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* إخفاء القوائم وأدوات المطور */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stHeader"] {visibility: hidden !important;}
    .stDeployButton {display: none !important;}

    /* إعدادات الخلفية */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* تنسيق زر البحث */
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
        color: white; border-radius: 8px; border: none; padding: 8px;
        font-size: 16px; font-weight: bold; transition: all 0.3s ease;
    }

    /* إعدادات الطباعة النظيفة */
    @media print {
        .print-hide, [data-testid="stSidebar"], header, footer, [data-testid="stForm"], button, hr, .stDivider {
            display: none !important;
        }
        
        html, body, .stApp, [data-testid="stAppViewContainer"], main, .block-container, [data-testid="stAppViewBlockContainer"] {
            background: white !important;
            background-color: #ffffff !important;
            background-image: none !important;
            color: black !important;
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }

        .receipt-container {
            display: block !important;
            position: absolute !important;
            top: 20px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 90% !important;
            max-width: 600px !important;
            border: 2px solid #000 !important;
            box-shadow: none !important;
            page-break-inside: avoid !important;
        }

        @page { size: A4 portrait; margin: 10mm; }
        * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='text-align: center; direction: rtl;'>⚙️ الإدارة</h3>", unsafe_allow_html=True)
    password = st.text_input("رمز المرور:", type="password", key="admin_pass")
    if password == "1234":
        st.success("✅ تم الدخول")
        uploaded_file = st.file_uploader("📂 رفع ملف Excel:", type=["xlsx", "xls"])
        if uploaded_file is not None:
            with open("salaries.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✨ تم التحديث بنجاح!")

st.markdown("""
<div class="print-hide" style='background: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; border: 1px solid #cbd5e1; margin-top: 30px;'>
    <h2 style='color: #0f172a; margin: 0;'>🏛️ بوابة الرواتب الإلكترونية</h2>
    <h4 style='color: #475569; margin-top: 5px; font-weight: normal;'>جامعة ابن سينا للعلوم الطبية والصيدلانية</h4>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    with st.form(key='search_form'):
        emp_id = st.text_input("الرقم الوظيفي", placeholder="أدخل الرقم الوظيفي هنا...", label_visibility="collapsed")
        search_button = st.form_submit_button("🔐 عرض كشف الراتب", use_container_width=True)

st.write("---")

if search_button:
    if not emp_id.strip():
        st.warning("⚠️ يرجى كتابة الرقم الوظيفي أولاً.")
    elif not os.path.exists("salaries.xlsx"):
        st.error("❌ ملف قاعدة البيانات غير موجود. الرجاء رفع الملف من لوحة الإدارة.")
    else:
        try:
            df = pd.read_excel("salaries.xlsx")
            if 'الرقم الوظيفي' not in df.columns:
                st.error("❌ لا يوجد عمود باسم 'الرقم الوظيفي' في ملف الإكسيل.")
            else:
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                search_query = str(emp_id).strip()
                user_data = df[df['الرقم الوظيفي'] == search_query]
                
                if not user_data.empty:
                    row = user_data.iloc[0]
                    
                    html_unified_card = f"""
<div class="receipt-container" style="direction: rtl; background: white; border-radius: 10px; padding: 25px; border: 2px solid #cbd5e1; max-width: 550px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
<div style="text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 15px; margin-bottom: 20px;">
<h3 style="color: #0f172a; margin: 0; font-size: 22px;">🧾 وصل استلام راتب</h3>
<div style="color: #64748b; font-size: 14px; margin-top: 5px;">كشف مفردات الراتب الشهري</div>
</div>
<table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: right; margin-bottom: 25px;">
<tbody>
<tr>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; width: 25%; color: #475569;">الاسم</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;" colspan="3">{row.get('الاسم', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; width: 25%; color: #475569;">الرقم الوظيفي</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1; width: 25%;">{row.get('الرقم الوظيفي', '-')}</td>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; width: 25%; color: #475569;">اللقب العلمي</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1; width: 25%;">{row.get('اللقب العلمي', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; color: #475569;">المنصب</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;" colspan="3">{row.get('المنصب', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; width: 25%; color: #475569;">الدرجة الوظيفية</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1; width: 25%;">{row.get('الدرجة الوظيفية', '-')}</td>
<td style="padding: 8px; font-weight: bold; background-color: #f1f5f9; border: 1px solid #cbd5e1; width: 25%; color: #475569;">المرحلة</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1; width: 25%;">{row.get('المرحلة', '-')}</td>
</tr>
</tbody>
</table>
<div style="font-weight: bold; color: #334155; margin-bottom: 10px; font-size: 15px;">📊 تفاصيل المستحقات والاستقطاعات:</div>
<table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: right;">
<tbody>
<tr>
<td style="padding: 8px; font-weight: bold; color: #475569; width: 45%; border: 1px solid #cbd5e1; background-color: #f8fafc;">الراتب الاسمي</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;">{row.get('الراتب الاسمي', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #475569; border: 1px solid #cbd5e1; background-color: #f8fafc;">الخدمة الجامعية</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;">{row.get('الخدمة الجامعية', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #475569; border: 1px solid #cbd5e1; background-color: #f8fafc;">النقل</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;">{row.get('النقل', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #475569; border: 1px solid #cbd5e1; background-color: #f8fafc;">الزوجية</td>
<td style="padding: 8px; font-weight: bold; color: #1e293b; border: 1px solid #cbd5e1;">{row.get('الزوجية', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #0369a1; border: 1px solid #93c5fd; background-color: #eff6ff;">الراتب الكامل</td>
<td style="padding: 8px; font-weight: bold; color: #0369a1; border: 1px solid #93c5fd; background-color: #eff6ff;">{row.get('الراتب الكامل', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #b91c1c; border: 1px solid #fca5a5; background-color: #fef2f2;">التقاعد (استقطاع)</td>
<td style="padding: 8px; font-weight: bold; color: #ef4444; border: 1px solid #fca5a5; background-color: #fef2f2;">{row.get('التقاعد', '-')}</td>
</tr>
<tr>
<td style="padding: 8px; font-weight: bold; color: #b91c1c; border: 1px solid #fca5a5; background-color: #fef2f2;">الضريبة (استقطاع)</td>
<td style="padding: 8px; font-weight: bold; color: #ef4444; border: 1px solid #fca5a5; background-color: #fef2f2;">{row.get('الضريبة', '-')}</td>
</tr>
<tr>
<td style="padding: 12px 8px; font-weight: 900; color: #059669; border: 2px solid #10b981; background-color: #ecfdf5; font-size: 16px;">الصافي للاستلام (د.ع)</td>
<td style="padding: 12px 8px; font-weight: 900; color: #059669; border: 2px solid #10b981; background-color: #ecfdf5; font-size: 20px;">{row.get('الراتب الصافي بعد الاستقطاعات', '-')}</td>
</tr>
</tbody>
</table>
</div>
"""
                    st.markdown(html_unified_card, unsafe_allow_html=True)

                    components.html(
                        """
                        <div class="print-hide" style="text-align: center; margin-top: 25px;">
                            <button onclick="window.parent.print()" style="background: linear-gradient(90deg, #334155 0%, #0f172a 100%); color: white; border-radius: 6px; border: none; padding: 10px 30px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);">
                                🖨️ طباعة وصل الراتب
                            </button>
                        </div>
                        """, height=80
                    )
                else:
                    st.error("❌ لم يتم العثور على موظف بهذا الرقم الوظيفي.")
                    
        except Exception as e:
            st.error("⚠️ حدث خطأ أثناء معالجة البيانات.")