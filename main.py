from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# --- الإعدادات ---
ADMIN_PASSWORD = "UISM_2026_ADMIN" 
LOCAL_FILE = "salaries.xlsx"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        :root { --primary: #1e40af; --secondary: #64748b; --accent: #10b981; --bg: #f1f5f9; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); margin: 0; padding: 20px; color: #1e293b; }
        .container { max-width: 750px; margin: 0 auto; }
        
        .search-card { background: white; border-radius: 24px; padding: 40px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 30px; }
        .header h2 { color: var(--primary); margin: 0; font-size: 26px; font-weight: 800; }
        
        input[type="text"], input[type="password"] { width: 100%; max-width: 400px; padding: 16px; border-radius: 12px; border: 2px solid #e2e8f0; font-size: 16px; text-align: center; margin-bottom: 10px; box-sizing: border-box; }
        .btn-search { background: var(--primary); color: white; padding: 16px; border-radius: 12px; border: none; font-size: 18px; font-weight: 700; cursor: pointer; width: 100%; max-width: 400px; transition: 0.3s; }
        .btn-search:hover { background: #1e3a8a; transform: translateY(-2px); }

        /* الجدول المذهل */
        .salary-card { background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); animation: fadeIn 0.6s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .table-header { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 25px; text-align: center; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 18px 25px; border-bottom: 1px solid #f1f5f9; font-size: 16px; }
        .label { color: #64748b; font-weight: 600; width: 45%; }
        .value { color: #0f172a; font-weight: 700; text-align: left; }

        /* تمييز صافي الراتب */
        .highlight { background: #f0fdf4 !important; }
        .highlight td { color: #15803d !important; font-size: 20px !important; font-weight: 900; border-bottom: none; }

        .admin-footer { margin-top: 50px; text-align: center; padding: 20px; border-top: 1px dashed #cbd5e1; opacity: 0.8; }
        @media print { .no-print { display: none !important; } body { background: white; } .salary-card { box-shadow: none; border: 1px solid #eee; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="search-card no-print">
            <div class="header">
                <h2>🏛️ جامعة ابن سينا</h2>
                <p>بوابة الاستعلام الإلكتروني عن الرواتب</p>
            </div>
            <form method="POST">
                <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي..." required>
                <button type="submit" class="btn-search">عرض الكشف الآن ➜</button>
            </form>
        </div>

        {% if msg %}<div style="text-align:center; color:#dc2626; margin-bottom:20px; font-weight:bold;">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="salary-card">
            <div class="table-header">
                <div style="font-size: 14px; opacity: 0.9;">كشف الراتب الرسمي للموظف</div>
                <div style="font-size: 22px; font-weight: bold; margin-top: 5px;">{{ data.get('الاسم', 'الموظف') }}</div>
            </div>
            <table>
                {% for key, value in data.items() if key != 'الاسم' %}
                <tr class="{{ 'highlight' if 'صافي' in key or 'استلام' in key else '' }}">
                    <td class="label">
                        {% if 'صافي' in key %}💰{% elif 'استقطاع' in key %}📉{% else %}•{% endif %} {{ key }}
                    </td>
                    <td class="value">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <button onclick="window.print()" class="btn-search no-print" style="background:#334155; margin-top:20px; max-width:100%;">🖨️ طباعة الكشف</button>
        {% endif %}

        <div class="admin-footer no-print">
            <p style="font-size:12px;">⚙️ قسم الإدارة</p>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="كلمة المرور" required style="max-width:200px; padding:8px;">
                <input type="file" name="file" accept=".xlsx" required style="font-size:11px;">
                <button type="submit" style="background:#475569; color:white; border:none; padding:8px 15px; border-radius:8px; cursor:pointer;">تحديث</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    msg, data = None, None
    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        if os.path.exists(LOCAL_FILE):
            try:
                df = pd.read_excel(LOCAL_FILE)
                df.columns = [str(c).strip() for c in df.columns]
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                res = df[df['الرقم الوظيفي'] == emp_id]
                if not res.empty:
                    data = res.iloc[0].to_dict()
                else:
                    msg = "❌ الرقم الوظيفي غير مسجل."
            except Exception as e:
                msg = "⚠️ حدث خطأ في معالجة الملف."
        else:
            msg = "⚠️ لم يتم رفع ملف الرواتب بعد."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('password') == ADMIN_PASSWORD:
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return render_template_string(HTML_TEMPLATE, msg="✅ تم التحديث بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="❌ فشل التحديث!")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
