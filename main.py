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
        :root { --primary: #2563eb; --bg: #f8fafc; --text: #1e293b; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--text); }
        .container { max-width: 600px; margin: 0 auto; }
        
        /* تصميم الكارت */
        .card { background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 30px; margin-bottom: 20px; border: 1px solid #f1f5f9; }
        .header { text-align: center; margin-bottom: 25px; }
        .header h2 { color: var(--primary); margin: 0; font-size: 22px; }
        
        .search-box { display: flex; flex-direction: column; gap: 12px; align-items: center; }
        input { width: 90%; padding: 14px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 16px; text-align: center; outline: none; transition: 0.3s; }
        input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1); }
        
        .btn { width: 95%; padding: 14px; border: none; border-radius: 12px; font-size: 17px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-print { background: #475569; color: white; margin-top: 15px; }

        /* تفاصيل الكارت الناتجة */
        .info-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
        .info-label { color: #64748b; font-weight: 500; }
        .info-value { font-weight: 600; color: var(--text); }

        /* المخطط البياني (Progress Bar) */
        .chart-container { margin: 25px 0; text-align: center; }
        .progress-bg { background: #e2e8f0; height: 12px; border-radius: 10px; overflow: hidden; margin-top: 10px; }
        .progress-fill { background: linear-gradient(90deg, #3b82f6, #10b981); height: 100%; border-radius: 10px; transition: 1s ease-out; }
        .percentage-text { font-size: 14px; color: #10b981; font-weight: bold; }

        .error { color: #dc2626; background: #fef2f2; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 1px solid #fee2e2; }
        .success { color: #16a34a; background: #f0fdf4; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }

        .admin-section { margin-top: 40px; text-align: center; opacity: 0.7; }
        .admin-section input { width: 70%; padding: 10px; font-size: 14px; }

        @media print { .no-print { display: none !important; } .card { box-shadow: none; border: 1px solid #eee; } body { background: white; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="card no-print">
            <div class="header">
                <h2>🏛️ جامعة ابن سينا</h2>
                <p style="font-size: 14px; color: #64748b;">بوابة استلام كشف الراتب الرقمي</p>
            </div>
            <form method="POST" class="search-box">
                <input type="text" name="emp_id" placeholder="أدخل الرقم الوظيفي..." required>
                <button type="submit" class="btn btn-primary">🔍 استعلام الآن</button>
            </form>
        </div>

        {% if msg %}<div class="{{ 'success' if 'تم' in msg else 'error' }}">{{ msg }}</div>{% endif %}

        {% if data %}
        <div class="card" id="print-area">
            <div style="text-align: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 15px; margin-bottom: 15px;">
                <span style="font-size: 12px; color: #94a3b8;">وصل استحقاق راتب شهر مارس 2026</span>
                <h3 style="margin: 5px 0; color: #1e293b;">{{ data.get('الاسم', 'الموظف') }}</h3>
            </div>

            {% for key, value in data.items() if key != 'الاسم' %}
                {% if 'صافي' in key or 'استلام' in key %}
                    <div class="chart-container">
                        <div style="display: flex; justify-content: space-between;">
                            <span class="info-label">{{ key }}</span>
                            <span class="percentage-text">{{ value }} د.ع</span>
                        </div>
                        <div class="progress-bg"><div class="progress-fill" style="width: 100%;"></div></div>
                        <p style="font-size: 11px; color: #94a3b8; margin-top: 5px;">تم احتساب كافة الاستقطاعات الضريبية والتقاعدية</p>
                    </div>
                {% else %}
                    <div class="info-row">
                        <span class="info-label">{{ key }}</span>
                        <span class="info-value">{{ value }}</span>
                    </div>
                {% endif %}
            {% endfor %}

            <button onclick="window.print()" class="btn btn-print no-print">🖨️ طباعة الكارت</button>
        </div>
        {% endif %}

        <div class="admin-section no-print">
            <p style="font-size: 12px;">⚙️ تحديث البيانات (للمصرح لهم)</p>
            <form method="POST" action="/upload" enctype="multipart/form-data" style="display: flex; flex-direction: column; gap: 8px; align-items: center;">
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <input type="file" name="file" accept=".xlsx" required>
                <button type="submit" class="btn" style="background: #1e293b; color: white; width: 75%;">تحديث الملف</button>
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
                else: msg = "❌ الرقم الوظيفي غير موجود."
            except: msg = "⚠️ خطأ في قراءة البيانات."
        else: msg = "⚠️ يرجى رفع ملف الرواتب أولاً."
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
