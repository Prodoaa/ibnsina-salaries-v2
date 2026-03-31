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
        :root { --primary: #1e3a8a; --accent: #10b981; --border: #e2e8f0; --bg: #f8fafc; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }

        /* كارت البحث */
        .card-search { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; margin-bottom: 25px; }
        input[type="text"] { width: 100%; padding: 15px; border-radius: 12px; border: 2px solid var(--border); font-size: 16px; text-align: center; box-sizing: border-box; }
        .btn-main { background: var(--primary); color: white; border: none; padding: 15px 30px; border-radius: 12px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 15px; font-size: 17px; }

        /* تصميم المخطط (Timeline) */
        .salary-chart-card { background: white; border-radius: 24px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); position: relative; }
        .employee-name { text-align: center; color: var(--primary); font-size: 24px; font-weight: 800; margin-bottom: 30px; border-bottom: 2px solid var(--bg); padding-bottom: 15px; }

        .timeline { position: relative; margin-right: 20px; border-right: 3px solid #e2e8f0; padding: 10px 0; }
        .item { position: relative; margin-bottom: 25px; padding-right: 35px; }
        
        /* الدوائر في المخطط */
        .item::before { 
            content: ''; position: absolute; right: -9px; top: 5px; 
            width: 15px; height: 15px; background: white; 
            border: 3px solid var(--primary); border-radius: 50%; z-index: 2; 
        }

        .item-content { display: flex; justify-content: space-between; align-items: center; background: #fdfdfd; padding: 12px 18px; border-radius: 15px; border: 1px solid #f1f5f9; }
        .item-label { color: #64748b; font-size: 15px; font-weight: 600; }
        .item-value { color: #1e293b; font-weight: 700; font-family: 'Courier New', monospace; }

        /* تمييز الصافي */
        .net-item::before { border-color: var(--accent); background: var(--accent); }
        .net-item .item-content { background: #ecfdf5; border: 1px solid #bbf7d0; padding: 20px 18px; }
        .net-item .item-label { color: #065f46; font-size: 18px; }
        .net-item .item-value { color: #047857; font-size: 22px; }

        .admin-box { margin-top: 50px; text-align: center; border-top: 1px dashed #cbd5e1; padding-top: 20px; }
        .admin-box input { font-size: 12px; margin-bottom: 5px; }

        @media print { .no-print { display: none !important; } .salary-chart-card { box-shadow: none; border: 1px solid #eee; } }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="card-search no-print">
            <h2 style="margin:0 0 10px 0; color:var(--primary);">🏛️ جامعة ابن سينا</h2>
            <p style="margin:0 0 20px 0; color:#64748b; font-size:14px;">نظام عرض الرواتب المخطط</p>
            <form method="POST">
                <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي..." required>
                <button type="submit" class="btn-main">استعلام عن التفاصيل</button>
            </form>
        </div>

        {% if msg %}<div style="text-align:center; color:#ef4444; margin-bottom:20px;">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="salary-chart-card">
            <div class="employee-name">{{ data.get('الاسم', 'موظف الجامعة') }}</div>
            
            <div class="timeline">
                {% for key, value in data.items() if key != 'الاسم' %}
                <div class="item {{ 'net-item' if 'صافي' in key or 'استلام' in key else '' }}">
                    <div class="item-content">
                        <span class="item-label">{{ key }}</span>
                        <span class="item-value">{{ value }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <button onclick="window.print()" class="btn-main no-print" style="background:#334155;">🖨️ طباعة المخطط الرسمي</button>
        </div>
        {% endif %}

        <div class="admin-box no-print">
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="كلمة المرور" required><br>
                <input type="file" name="file" accept=".xlsx" required><br>
                <button type="submit" style="background:#475569; color:white; border:none; padding:8px 15px; border-radius:8px; cursor:pointer; margin-top:5px;">تحديث القاعدة</button>
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
                # تنظيف أسماء الأعمدة من أي مسافات مخفية
                df.columns = [str(c).strip() for c in df.columns]
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                res = df[df['الرقم الوظيفي'] == emp_id]
                if not res.empty:
                    data = res.iloc[0].to_dict()
                else:
                    msg = "❌ لم يتم العثور على هذا الرقم الوظيفي."
            except:
                msg = "⚠️ يوجد مشكلة في ملف الإكسل المرفوع."
        else:
            msg = "⚠️ لم يتم رفع ملف الرواتب بعد."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('password') == ADMIN_PASSWORD:
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return render_template_string(HTML_TEMPLATE, msg="✅ تم تحديث البيانات بنجاح!")
    return render_template_string(HTML_TEMPLATE, msg="❌ فشل التحديث: كلمة مرور خاطئة أو ملف غير صحيح.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
