from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# واجهة الموقع (HTML + CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%); margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .header { text-align: center; border-bottom: 2px solid #cbd5e1; padding-bottom: 20px; margin-bottom: 20px; }
        .header h2 { color: #0f172a; margin: 0; }
        .header h4 { color: #475569; margin-top: 5px; font-weight: normal; }
        
        .search-box { display: flex; flex-direction: column; gap: 15px; margin-bottom: 30px; align-items: center; }
        input[type="text"] { padding: 12px; width: 80%; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; text-align: center; }
        button { background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 80%; }
        button:hover { opacity: 0.9; }
        
        .receipt { border: 2px solid #cbd5e1; padding: 25px; border-radius: 10px; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px; text-align: right; }
        td { padding: 10px; border: 1px solid #cbd5e1; }
        .bg-light { background-color: #f1f5f9; font-weight: bold; width: 30%; color: #475569; }
        .val { color: #1e293b; font-weight: bold; }
        .error { color: #b91c1c; background: #fef2f2; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #fca5a5; margin-bottom: 20px; font-weight: bold;}
        
        @media print {
            body { background: white; padding: 0; }
            .no-print { display: none !important; }
            .container { box-shadow: none; border: none; padding: 0; max-width: 100%; }
            .receipt { border: 2px solid #000; padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header no-print">
            <h2>🏛️ بوابة الرواتب الإلكترونية</h2>
            <h4>جامعة ابن سينا للعلوم الطبية والصيدلانية</h4>
        </div>
        
        <form method="POST" class="search-box no-print">
            <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي هنا..." required value="{{ emp_id or '' }}">
            <button type="submit">🔐 عرض كشف الراتب</button>
        </form>

        {% if error %}
            <div class="error no-print">{{ error }}</div>
        {% endif %}

        {% if data %}
        <div class="receipt">
            <div style="text-align: center; margin-bottom: 25px; border-bottom: 2px solid #0f172a; padding-bottom: 15px;">
                <h3 style="margin: 0; font-size: 22px;">🧾 وصل استلام راتب</h3>
                <div style="color: #64748b; margin-top: 5px;">كشف مفردات الراتب الشهري</div>
            </div>
            
            <table>
                <tr><td class="bg-light">الاسم</td><td colspan="3" class="val">{{ data.get('الاسم', '-') }}</td></tr>
                <tr>
                    <td class="bg-light">الرقم الوظيفي</td><td class="val">{{ data.get('الرقم الوظيفي', '-') }}</td>
                    <td class="bg-light">اللقب العلمي</td><td class="val">{{ data.get('اللقب العلمي', '-') }}</td>
                </tr>
                <tr><td class="bg-light">المنصب</td><td colspan="3" class="val">{{ data.get('المنصب', '-') }}</td></tr>
                <tr>
                    <td class="bg-light">الدرجة الوظيفية</td><td class="val">{{ data.get('الدرجة الوظيفية', '-') }}</td>
                    <td class="bg-light">المرحلة</td><td class="val">{{ data.get('المرحلة', '-') }}</td>
                </tr>
            </table>
            
            <h4 style="color: #334155; margin-bottom: 10px;">📊 تفاصيل المستحقات والاستقطاعات:</h4>
            <table>
                <tr><td class="bg-light">الراتب الاسمي</td><td class="val">{{ data.get('الراتب الاسمي', '-') }}</td></tr>
                <tr><td class="bg-light">الخدمة الجامعية</td><td class="val">{{ data.get('الخدمة الجامعية', '-') }}</td></tr>
                <tr><td class="bg-light">النقل</td><td class="val">{{ data.get('النقل', '-') }}</td></tr>
                <tr><td class="bg-light">الزوجية</td><td class="val">{{ data.get('الزوجية', '-') }}</td></tr>
                <tr style="background-color: #eff6ff;"><td class="bg-light" style="color: #0369a1;">الراتب الكامل</td><td class="val" style="color: #0369a1;">{{ data.get('الراتب الكامل', '-') }}</td></tr>
                <tr style="background-color: #fef2f2;"><td class="bg-light" style="color: #b91c1c;">التقاعد (استقطاع)</td><td class="val" style="color: #ef4444;">{{ data.get('التقاعد', '-') }}</td></tr>
                <tr style="background-color: #fef2f2;"><td class="bg-light" style="color: #b91c1c;">الضريبة (استقطاع)</td><td class="val" style="color: #ef4444;">{{ data.get('الضريبة', '-') }}</td></tr>
                <tr style="background-color: #ecfdf5;"><td class="bg-light" style="color: #059669; font-size: 16px;">الصافي للاستلام (د.ع)</td><td class="val" style="color: #059669; font-size: 20px;">{{ data.get('الراتب الصافي بعد الاستقطاعات', '-') }}</td></tr>
            </table>
        </div>
        
        <div class="no-print" style="text-align: center; margin-top: 25px;">
            <button onclick="window.print()" style="background: #0f172a; width: auto; padding: 10px 30px;">🖨️ طباعة وصل الراتب</button>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    data = None
    emp_id = ""

    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        
        # التأكد من وجود ملف الإكسيل
        if not os.path.exists("salaries.xlsx"):
            error = "⚠️ ملف قاعدة البيانات (salaries.xlsx) غير موجود."
        else:
            try:
                # قراءة ملف الإكسيل
                df = pd.read_excel("salaries.xlsx")
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                
                # البحث عن الموظف
                user_data = df[df['الرقم الوظيفي'] == emp_id]
                
                if not user_data.empty:
                    data = user_data.iloc[0].to_dict()
                else:
                    error = "❌ لم يتم العثور على موظف بهذا الرقم الوظيفي."
            except Exception as e:
                error = "⚠️ حدث خطأ أثناء معالجة ملف الإكسيل."

    return render_template_string(HTML_TEMPLATE, error=error, data=data, emp_id=emp_id)

if __name__ == '__main__':
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
