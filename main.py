from flask import Flask, request, render_template_string, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# --- الإعدادات ---
ADMIN_PASSWORD = "UISM_2026_ADMIN" 
LOCAL_FILE = "salaries.xlsx"
LOGO_FILENAME = "logo.png"  # اسم ملف الشعار في المستودع

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        :root {
            --primary-color: #1a4b8f; /* أزرق ملكي كلاسيكي */
            --accent-color: #047857;  /* أخضر زمردي للصافي */
            --bg-color: #f3f6f9;
            --table-border-dark: #374151; /* حدود بارزة وواضحة جداً */
            --table-border-light: #cbd5e1;
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
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
            text-align: center;
            border-top: 6px solid var(--primary-color);
        }

        /* شعار الجامعة */
        .uism-logo { max-width: 150px; margin-bottom: 15px; }

        h2.university-name { color: var(--primary-color); margin: 0 0 5px 0; font-weight: 800; font-size: 26px;}
        p.subtitle { color: #64748b; margin: 0 0 25px 0; font-size: 14px; }

        .input-box {
            width: 100%; max-width: 400px; padding: 15px;
            border: 2px solid #d1d5db; border-radius: 12px;
            font-size: 16px; text-align: center; outline: none;
            transition: all 0.3s;
        }
        .input-box:focus { border-color: var(--primary-color); box-shadow: 0 0 0 4px rgba(26, 75, 143, 0.1); }

        .btn-action {
            background: var(--primary-color); color: white; border: none;
            padding: 15px 40px; border-radius: 12px; font-size: 17px;
            font-weight: bold; cursor: pointer; margin-top: 15px;
            width: 100%; max-width: 400px; transition: background-color 0.2s;
        }
        .btn-action:hover { background-color: #163f7a; }

        /* الجدول الفاخر والواضح جداً */
        .salary-table-wrapper {
            background: white; border-radius: 20px; overflow: hidden;
            box-shadow: 0 15px 20px -5px rgba(0, 0, 0, 0.08);
            border: 2px solid var(--table-border-dark); /* إطار خارجي قوي */
        }

        .table-title {
            background: var(--primary-color); color: white;
            padding: 20px; font-size: 20px; font-weight: 800;
            text-align: center; border-bottom: 2px solid var(--table-border-dark);
        }

        table { width: 100%; border-collapse: collapse; background: white; table-layout: fixed; }

        th, td {
            padding: 20px 25px; text-align: right;
            border: 1.5px solid var(--table-border-dark); /* خطوط شبكية بارزة جداً */
            word-wrap: break-word;
        }

        tr:nth-child(even) { background-color: #f8fafc; }

        .row-label {
            color: #1e293b; font-weight: 700; width: 45%;
            background-color: #f1f5f9; /* تباين أفضل للعناوين */
        }

        .row-value { color: #0f172a; font-weight: 700; text-align: left; }

        /* تمييز صافي الراتب بوضوح فائق */
        .net-salary-row { background: #d1fae5 !important; }
        .net-salary-row .row-label, .net-salary-row .row-value {
            color: var(--accent-color) !important; font-size: 22px; font-weight: 900;
            padding: 28px 25px;
        }

        .btn-print {
            background: #475569; color: white; width: 100%;
            padding: 15px; border: none; border-radius: 12px;
            margin-top: 25px; font-weight: bold; cursor: pointer; font-size: 16px;
        }

        .admin-panel { margin-top: 50px; text-align: center; border-top: 1px dashed #cbd5e1; padding-top: 20px; opacity: 0.6; }

        @media print { .no-print { display: none !important; } .main-wrapper { padding: 0; } .salary-table-wrapper { box-shadow: none; border: 2.5px solid #000; } table, td, tr { border: 2px solid #000; } }
    </style>
</head>
<body>
    <div class="main-wrapper">
        
        <div class="search-container no-print">
            <img src="{{ url_for('get_logo') }}" alt="UISM Logo" class="uism-logo">
            <h2 class="university-name">جامعة ابن سينا للعلوم الطبية والصيدلانية</h2>
            <p class="subtitle">نظام الاستعلام الرسمي عن تفاصيل الرواتب - كشف إلكتروني معتمد</p>
            <form method="POST">
                <input type="text" name="emp_id" class="input-box" placeholder="أدخل الرقم الوظيفي هنا..." required>
                <br>
                <button type="submit" class="btn-action">🔍 استخراج كشف الراتب</button>
            </form>
        </div>

        {% if msg %}<div style="text-align:center; color:#dc2626; margin-bottom:20px; font-weight:bold;">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="salary-table-wrapper">
            <div class="table-title">كشف مفردات الراتب باسم: {{ data.get('الاسم', 'الموظف المحترم') }}</div>
            <table>
                {% for key, value in data.items() if key != 'الاسم' %}
                <tr class="{{ 'net-salary-row' if 'صافي' in key or 'استلام' in key else '' }}">
                    <td class="row-label">{{ key }}</td>
                    <td class="row-value">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <button onclick="window.print()" class="btn-print no-print">🖨️ طباعة المستند الرسمي للجامعة</button>
        {% endif %}

        <div class="admin-panel no-print">
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="كلمة المرور" required style="padding:5px; border-radius:5px; border:1px solid #ccc;">
                <input type="file" name="file" accept=".xlsx" required style="font-size:11px;">
                <button type="submit" style="cursor:pointer;">تحديث البيانات</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def route_index():
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

# دالة لتمرير الشعار كصورة
@app.route('/logo.png')
def get_logo():
    if os.path.exists(LOGO_FILENAME):
        return send_from_directory(os.getcwd(), LOGO_FILENAME)
    return '', 404

@app.route('/', methods=['POST'])
def index():
    return route_index()

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
