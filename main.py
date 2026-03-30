from flask import Flask, request, render_template_string, redirect
import pandas as pd
import os

app = Flask(__name__)

# --- إعدادات الأمان ---
ADMIN_PASSWORD = "UISM_2026_ADMIN"  # يمكنك تغيير كلمة المرور من هنا
UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'xlsx'}

# واجهة الموقع المحدثة (HTML + CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f4f8; margin: 0; padding: 20px; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .header { text-align: center; border-bottom: 2px solid #cbd5e1; padding-bottom: 20px; margin-bottom: 20px; }
        .search-box { display: flex; flex-direction: column; gap: 15px; margin-bottom: 30px; align-items: center; }
        input[type="text"], input[type="password"], input[type="file"] { padding: 12px; width: 80%; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; text-align: center; }
        button { background: #0284c7; color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; width: 80%; }
        .receipt { border: 2px solid #cbd5e1; padding: 25px; border-radius: 10px; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; text-align: right; }
        td { padding: 10px; border: 1px solid #cbd5e1; }
        .bg-light { background-color: #f1f5f9; font-weight: bold; width: 35%; }
        .error { color: #b91c1c; background: #fef2f2; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
        .success { color: #059669; background: #ecfdf5; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
        
        /* قسم الإدارة المخفي */
        .admin-section { margin-top: 50px; border-top: 2px dashed #cbd5e1; padding-top: 20px; text-align: center; opacity: 0.6; }
        .admin-section:hover { opacity: 1; }
        
        @media print { .no-print { display: none !important; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header no-print">
            <h2>🏛️ بوابة الرواتب الإلكترونية</h2>
            <h4>جامعة ابن سينا للعلوم الطبية والصيدلانية</h4>
        </div>
        
        <form method="POST" action="/" class="search-box no-print">
            <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي..." required>
            <button type="submit">🔐 عرض كشف الراتب</button>
        </form>

        {% if msg %}<div class="{{ 'success' if 'تم' in msg else 'error' }}">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="receipt">
            <h3 style="text-align: center;">🧾 وصل استلام راتب</h3>
            <table>
                <tr><td class="bg-light">الاسم</td><td class="val">{{ data.get('الاسم', '-') }}</td></tr>
                <tr><td class="bg-light">الرقم الوظيفي</td><td class="val">{{ data.get('الرقم الوظيفي', '-') }}</td></tr>
                <tr><td class="bg-light">الصافي للاستلام</td><td class="val" style="color: #059669; font-size: 20px; font-weight: bold;">{{ data.get('الراتب الصافي بعد الاستقطاعات', '-') }} د.ع</td></tr>
            </table>
            <button onclick="window.print()" class="no-print" style="background: #334155;">🖨️ طباعة</button>
        </div>
        {% endif %}

        <div class="admin-section no-print">
            <p>⚙️ قسم إدارة البيانات (للمصرح لهم فقط)</p>
            <form method="POST" action="/upload" enctype="multipart/form-data" class="search-box">
                <input type="password" name="password" placeholder="كلمة مرور الإدارة" required>
                <input type="file" name="file" accept=".xlsx" required>
                <button type="submit" style="background: #1e293b;">📤 تحديث قاعدة بيانات الرواتب</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = None
    data = None
    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        if not os.path.exists("salaries.xlsx"):
            msg = "⚠️ قاعدة البيانات غير متوفرة حالياً."
        else:
            try:
                df = pd.read_excel("salaries.xlsx")
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                user_data = df[df['الرقم الوظيفي'] == emp_id]
                if not user_data.empty:
                    data = user_data.iloc[0].to_dict()
                else:
                    msg = "❌ الرقم الوظيفي غير موجود."
            except:
                msg = "⚠️ خطأ في قراءة ملف البيانات."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.form.get('password')
    file = request.files.get('file')
    
    if password != ADMIN_PASSWORD:
        return render_template_string(HTML_TEMPLATE, msg="❌ كلمة مرور خاطئة!")
    
    if file and file.filename.endswith('.xlsx'):
        file.save(os.path.join(UPLOAD_FOLDER, "salaries.xlsx"))
        return render_template_string(HTML_TEMPLATE, msg="✅ تم تحديث ملف الرواتب بنجاح!")
    
    return render_template_string(HTML_TEMPLATE, msg="⚠️ يرجى اختيار ملف Excel صحيح.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
