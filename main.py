from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# --- إعدادات النظام ---
ADMIN_PASSWORD = "UISM_2026_ADMIN"  # كلمة مرور الإدارة (يمكنك تغييرها)
LOCAL_FILE = "salaries.xlsx"

# واجهة الموقع
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f9; margin: 0; padding: 20px; color: #334155; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #0284c7; padding-bottom: 20px; margin-bottom: 30px; }
        .header h2 { color: #0284c7; margin: 0; }
        .search-box { display: flex; flex-direction: column; gap: 15px; margin-bottom: 30px; align-items: center; }
        input { padding: 12px; width: 85%; border: 2px solid #e2e8f0; border-radius: 10px; font-size: 16px; text-align: center; outline: none; }
        .btn-search { background: #0284c7; color: white; border: none; padding: 12px; width: 85%; border-radius: 10px; cursor: pointer; font-size: 18px; font-weight: bold; }
        
        .receipt { border: 2px solid #e2e8f0; padding: 20px; border-radius: 12px; background: #fff; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 15px; }
        .label { background: #f8fafc; font-weight: bold; width: 45%; color: #64748b; }
        .value { color: #1e293b; font-weight: 500; text-align: left; }
        .total-row { background: #f0fdf4 !important; font-weight: bold; color: #166534; }

        .error { color: #b91c1c; background: #fef2f2; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #fecaca; }
        .success { color: #15803d; background: #f0fdf4; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #bbf7d0; }

        .admin-panel { margin-top: 60px; border-top: 2px dashed #cbd5e1; padding-top: 30px; }
        .admin-title { font-size: 14px; color: #94a3b8; text-align: center; margin-bottom: 15px; }
        
        @media print { .no-print { display: none !important; } .container { box-shadow: none; width: 100%; padding: 0; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header no-print">
            <h2>🏛️ جامعة ابن سينا للعلوم الطبية والصيدلانية</h2>
            <p>نظام الاستعلام عن الرواتب - موظفي الجامعة</p>
        </div>
        
        <form method="POST" action="/" class="search-box no-print">
            <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي..." required>
            <button type="submit" class="btn-search">🔍 عرض كشف الراتب</button>
        </form>

        {% if msg %}<div class="{{ 'success' if 'تم' in msg else 'error' }}">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="receipt">
            <h3 style="text-align: center;">🧾 تفاصيل الراتب الاستحقاقي</h3>
            <table>
                {% for key, value in data.items() %}
                <tr class="{{ 'total-row' if 'صافي' in key or 'الاستلام' in key else '' }}">
                    <td class="label">{{ key }}</td>
                    <td class="value">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <button onclick="window.print()" class="btn-search no-print" style="background: #475569; width: 100%;">🖨️ طباعة الكشف</button>
        </div>
        {% endif %}

        <div class="admin-panel no-print">
            <div class="admin-title">⚙️ بوابة موظف المالية (لرفع الملف الجديد)</div>
            <form method="POST" action="/upload" enctype="multipart/form-data" class="search-box">
                <input type="password" name="password" placeholder="كلمة المرور الإدارية" required style="width: 70%;">
                <input type="file" name="file" accept=".xlsx" required style="width: 70%;">
                <button type="submit" style="background: #1e293b; width: 70%;" class="btn-search">📤 تحديث البيانات</button>
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
                    msg = "❌ الرقم الوظيفي غير موجود في النظام."
            except Exception as e:
                msg = f"⚠️ خطأ في قراءة ملف الإكسل: {str(e)}"
        else:
            msg = "⚠️ لم يتم رفع ملف الرواتب بعد. يرجى رفعه من قسم الإدارة بالأسفل."
            
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.form.get('password')
    file = request.files.get('file')
    if password != ADMIN_PASSWORD:
        return render_template_string(HTML_TEMPLATE, msg="❌ كلمة مرور خاطئة!")
    if file and file.filename.endswith('.xlsx'):
        file.save(LOCAL_FILE)
        return render_template_string(HTML_TEMPLATE, msg="✅ تم تحديث ملف الرواتب بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="⚠️ يرجى اختيار ملف Excel صحيح بصيغة .xlsx")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
