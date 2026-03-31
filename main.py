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
            --primary: #1e40af; /* أزرق ملكي */
            --secondary: #64748b;
            --accent: #10b981; /* أخضر للصافي */
            --bg: #f1f5f9;
        }

        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: var(--bg); 
            margin: 0; 
            padding: 20px; 
            color: #1e293b;
        }

        .container { max-width: 750px; margin: 0 auto; }

        /* كارت البحث */
        .search-card {
            background: white;
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.8);
        }

        .header h2 { color: var(--primary); margin: 0; font-size: 28px; font-weight: 800; }
        .header p { color: var(--secondary); margin-top: 8px; font-size: 15px; }

        .input-group { position: relative; margin-top: 25px; width: 100%; max-width: 450px; margin-left: auto; margin-right: auto; }
        
        input[type="text"] {
            width: 100%;
            padding: 16px 20px;
            border-radius: 16px;
            border: 2px solid #e2e8f0;
            font-size: 18px;
            text-align: center;
            transition: all 0.3s;
            box-sizing: border-box;
        }

        input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.1);
            outline: none;
        }

        .btn-search {
            margin-top: 15px;
            background: var(--primary);
            color: white;
            padding: 16px 40px;
            border-radius: 16px;
            border: none;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: 0.3s;
            width: 100%;
            max-width: 450px;
        }

        .btn-search:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(30, 64, 175, 0.2); }

        /* الجدول المذهل */
        .salary-table-card {
            background: white;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.1);
            animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        .table-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }

        table { width: 100%; border-collapse: collapse; }
        
        td { padding: 20px 25px; border-bottom: 1px solid #f1f5f9; font-size: 16px; }

        .field-name { color: #64748b; font-weight: 600; width: 45%; }
        .field-value { color: #0f172a; font-weight: 700; text-align: left; }

        /* تنسيق صف الصافي */
        .net-salary-row {
            background: #f0fdf4;
        }

        .net-salary-row td {
            color: #15803d !important;
            font-size: 22px !important;
            padding: 30px 25px;
            border-bottom: none;
        }

        .btn-print {
            background: #1e293b;
            color: white;
            padding: 15px;
            border-radius: 12px;
            width: 100%;
            margin-top: 20px;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }

        /* قسم الإدارة */
        .admin-footer { margin-top: 50px; text-align: center; padding: 20px; border-top: 1px dashed #cbd5e1; }
        .admin-footer input { padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 10px; }

        @media print { .no-print { display: none !important; } body { background: white; padding: 0; } .salary-table-card { box-shadow: none; border: 1px solid #eee; } }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="search-card no-print">
            <div class="header">
                <h2>🏛️ جامعة ابن سينا</h2>
                <p>للعلوم الطبية والصيدلانية - بوابة الرواتب</p>
            </div>
            <form method="POST" action="/">
                <div class="input-group">
                    <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي بدقة..." required>
                </div>
                <button type="submit" class="btn-search">كشف الراتب الآن ➜</button>
            </form>
        </div>

        {% if msg %}<div style="text-align:center; color:#ef4444; padding:10px; font-weight:bold;">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="salary-table-card">
            <div class="table-header">
                <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">كشف راتب الموظف الرسمي</div>
                <div style="font-size: 22px; font-weight: 800;">{{ data.get('الاسم', 'الموظف المحترم') }}</div>
            </div>
            <table>
                {% for key, value in data.items() if key != 'الاسم' %}
                <tr class="{{ 'net-salary-row' if 'صافي' in key or 'الاستلام' in key else '' }}">
                    <td class="field-name">
                        {% if 'صافي' in key %} 💰 {% elif 'استقطاع' in key %} 📉 {% elif 'مخصصات' in key %} ➕ {% else %} • {% endif %}
                        {{ key }}
                    </td>
                    <td class="field-value">{{ value }} {{ 'د.ع' if 'دينار' not in str(value) and any(x in key for x in ['راتب','مخصصات','استقطاع','صافي']) else '' }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <button onclick="window.print()" class="btn-print no-print">🖨️ طباعة كشف الراتب الرسمي</button>
        {% endif %}

        <div class="admin-footer no-print">
            <p style="font-size: 12px; color: #94a3b8;">⚙️ قسم تحديث البيانات (موظف المالية)</p>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <input type="file" name="file" accept=".xlsx" required style="font-size: 12px;">
                <button type="submit" style="background:#475569; color:white; border:none; padding:8px 20px; border-radius:8px; cursor:pointer;">تحديث الملف</button>
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
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                res = df[df['الرقم الوظيفي'] == emp_id]
                if not res.empty: data = res.iloc[0].to_dict()
                else: msg = "⚠️ لم يتم العثور على الرقم الوظيفي."
            except: msg = "⚠️ خطأ في قراءة ملف البيانات."
        else: msg = "⚠️ لم يتم رفع قاعدة البيانات بعد."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data, str=str, any=any)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('password') == ADMIN_PASSWORD:
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return render_template_string(HTML_TEMPLATE, msg="✅ تم التحديث بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="❌ عذراً، فشل التحديث.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
