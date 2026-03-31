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
        :root {
            --primary-color: #1e3a8a; /* أزرق غامق فاخر */
            --accent-color: #059669;  /* أخضر للصافي */
            --bg-color: #f3f4f6;
            --table-border: #e5e7eb;
        }

        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: var(--bg-color); 
            margin: 0; 
            padding: 40px 20px; 
            display: flex;
            justify-content: center;
        }

        .main-wrapper { width: 100%; max-width: 800px; }

        /* كارت الاستعلام */
        .search-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
            border-top: 5px solid var(--primary-color);
        }

        h2 { color: var(--primary-color); margin: 0 0 10px 0; }
        p.subtitle { color: #6b7280; margin: 0 0 25px 0; font-size: 14px; }

        .input-box {
            width: 100%;
            max-width: 400px;
            padding: 15px;
            border: 2px solid #d1d5db;
            border-radius: 10px;
            font-size: 16px;
            text-align: center;
            outline: none;
            transition: border-color 0.3s;
        }

        .input-box:focus { border-color: var(--primary-color); }

        .btn-action {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
            max-width: 400px;
        }

        /* الجدول الفاخر */
        .salary-table-wrapper {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        .table-title {
            background: var(--primary-color);
            color: white;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            padding: 18px 25px;
            text-align: right;
            border-bottom: 1px solid var(--table-border);
        }

        tr:nth-child(even) { background-color: #f9fafb; }

        .row-label {
            color: #4b5563;
            font-weight: 600;
            width: 40%;
            border-left: 1px solid var(--table-border);
        }

        .row-value {
            color: #111827;
            font-weight: 700;
            text-align: left; /* القيمة تظهر في اليسار والاسم في اليمين */
        }

        /* تمييز صافي الراتب */
        .net-salary-row {
            background: #ecfdf5 !important;
        }

        .net-salary-row .row-label, .net-salary-row .row-value {
            color: var(--accent-color) !important;
            font-size: 20px;
            padding: 25px;
        }

        .btn-print {
            background: #374151;
            color: white;
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            margin-top: 20px;
            font-weight: bold;
            cursor: pointer;
        }

        .admin-panel {
            margin-top: 50px;
            text-align: center;
            border-top: 1px dashed #ccc;
            padding-top: 20px;
            opacity: 0.6;
        }

        @media print { .no-print { display: none !important; } .salary-table-wrapper { box-shadow: none; border: 1px solid #000; } }
    </style>
</head>
<body>
    <div class="main-wrapper">
        
        <div class="search-container no-print">
            <h2>🏛️ جامعة ابن سينا</h2>
            <p class="subtitle">نظام الاستعلام الرسمي عن تفاصيل الرواتب</p>
            <form method="POST">
                <input type="text" name="emp_id" class="input-box" placeholder="أدخل الرقم الوظيفي هنا..." required>
                <br>
                <button type="submit" class="btn-action">🔍 استخراج كشف الراتب</button>
            </form>
        </div>

        {% if msg %}<div style="text-align:center; color:#dc2626; margin-bottom:20px; font-weight:bold;">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="salary-table-wrapper">
            <div class="table-title">كشف تفصيلي باسم: {{ data.get('الاسم', 'الموظف المحترم') }}</div>
            <table>
                {% for key, value in data.items() if key != 'الاسم' %}
                <tr class="{{ 'net-salary-row' if 'صافي' in key or 'استلام' in key else '' }}">
                    <td class="row-label">{{ key }}</td>
                    <td class="row-value">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <button onclick="window.print()" class="btn-print no-print">🖨️ طباعة المستند الرسمي</button>
        {% endif %}

        <div class="admin-panel no-print">
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="كلمة المرور" required style="padding:5px; border-radius:5px; border:1px solid #ccc;">
                <input type="file" name="file" accept=".xlsx" required style="font-size:12px;">
                <button type="submit" style="cursor:pointer;">تحديث البيانات</button>
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
                if not res.empty: data = res.iloc[0].to_dict()
                else: msg = "❌ الرقم الوظيفي غير موجود."
            except: msg = "⚠️ خطأ في قراءة ملف الإكسل."
        else: msg = "⚠️ قاعدة البيانات غير متوفرة حالياً."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('password') == ADMIN_PASSWORD:
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return render_template_string(HTML_TEMPLATE, msg="✅ تم التحديث بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="❌ فشل التحديث.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
