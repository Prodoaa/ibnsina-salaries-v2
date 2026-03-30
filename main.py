from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# --- الإعدادات ---
ADMIN_PASSWORD = "UISM_2026_ADMIN" 
LOCAL_FILE = "salaries.xlsx"

# واجهة المستخدم بتنسيق أنيق ومنظم
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; color: #1a202c; }
        .container { max-width: 650px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #edf2f7; padding-bottom: 20px; }
        .header h2 { color: #2c5282; margin: 0; font-size: 24px; }
        .header p { color: #718096; margin-top: 5px; }
        
        .search-box { display: flex; flex-direction: column; gap: 15px; margin-bottom: 25px; align-items: center; }
        input[type="text"], input[type="password"] { width: 90%; padding: 14px; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 16px; text-align: center; transition: 0.3s; }
        input:focus { border-color: #3182ce; outline: none; box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1); }
        
        .btn { width: 90%; padding: 14px; border: none; border-radius: 8px; font-size: 17px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn-primary { background: #3182ce; color: white; }
        .btn-primary:hover { background: #2b6cb0; }
        .btn-print { background: #4a5568; color: white; margin-top: 15px; width: 100%; }
        
        .receipt { border: 1.5px solid #edf2f7; border-radius: 10px; overflow: hidden; margin-top: 20px; }
        .receipt-header { background: #f8fafc; padding: 15px; text-align: center; font-weight: bold; border-bottom: 1.5px solid #edf2f7; }
        
        table { width: 100%; border-collapse: collapse; }
        td { padding: 15px; border-bottom: 1px solid #edf2f7; font-size: 16px; }
        .label { background: #fbfcfd; color: #4a5568; font-weight: 600; width: 40%; }
        .value { color: #2d3748; text-align: left; padding-left: 20px; }
        
        /* تمييز صافي الراتب */
        .highlight { background: #f0fff4 !important; }
        .highlight td { color: #22543d; font-weight: bold; font-size: 18px; }

        .error { color: #c53030; background: #fff5f5; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; border: 1px solid #feb2b2; }
        .success { color: #2f855a; background: #f0fff4; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; border: 1px solid #9ae6b4; }

        .admin-zone { margin-top: 50px; padding-top: 30px; border-top: 2px dashed #e2e8f0; }
        .admin-label { text-align: center; font-size: 13px; color: #a0aec0; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }

        @media print { .no-print { display: none !important; } .container { box-shadow: none; width: 100%; padding: 0; } body { background: white; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header no-print">
            <h2>🏛️ جامعة ابن سينا</h2>
            <p>نظام الاستعلام الإلكتروني عن الرواتب</p>
        </div>
        
        <form method="POST" action="/" class="search-box no-print">
            <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي هنا..." required autocomplete="off">
            <button type="submit" class="btn btn-primary">🔍 عرض كشف الراتب</button>
        </form>

        {% if msg %}<div class="{{ 'success' if 'تم' in msg else 'error' }}">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="receipt">
            <div class="receipt-header">🧾 كشف راتب الموظف للشهر الحالي</div>
            <table>
                {% for key, value in data.items() %}
                <tr class="{{ 'highlight' if 'صافي' in key or 'استلام' in key else '' }}">
                    <td class="label">{{ key }}</td>
                    <td class="value">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <button onclick="window.print()" class="btn btn-print no-print">🖨️ طباعة الوصل</button>
        {% endif %}

        <div class="admin-zone no-print">
            <div class="admin-label">⚙️ قسم إدارة البيانات (موظف المالية)</div>
            <form method="POST" action="/upload" enctype="multipart/form-data" class="search-box">
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <input type="file" name="file" accept=".xlsx" required style="border:none; background:none; font-size:14px;">
                <button type="submit" class="btn" style="background: #2d3748; color: white;">📤 تحديث قاعدة البيانات</button>
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
        if os.path.exists(LOCAL_FILE):
            try:
                df = pd.read_excel(LOCAL_FILE)
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                user_data = df[df['الرقم الوظيفي'] == emp_id]
                if not user_data.empty:
                    data = user_data.iloc[0].to_dict()
                else:
                    msg = "❌ الرقم الوظيفي غير صحيح أو غير مسجل."
            except Exception as e:
                msg = f"⚠️ حدث خطأ أثناء قراءة الملف."
        else:
            msg = "⚠️ لم يتم رفع ملف البيانات بعد. يرجى مراجعة قسم الإدارة."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.form.get('password')
    file = request.files.get('file')
    if password != ADMIN_PASSWORD:
        return render_template_string(HTML_TEMPLATE, msg="❌ كلمة المرور غير صحيحة!")
    if file and file.filename.endswith('.xlsx'):
        file.save(LOCAL_FILE)
        return render_template_string(HTML_TEMPLATE, msg="✅ تم تحديث بيانات الرواتب بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="⚠️ يرجى اختيار ملف إكسل (.xlsx) فقط.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
