from flask import Flask, request, render_template_string, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# --- الإعدادات الأمنية والملفات ---
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
        body { 
            font-family: 'Arial', 'Tahoma', sans-serif; 
            background-color: #f0f2f5; 
            margin: 0; padding: 20px; color: #333;
        }
        .container { max-width: 650px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        
        /* الترويسة والشعار */
        .header { text-align: center; border-bottom: 2.5px solid #1a4b8f; padding-bottom: 15px; margin-bottom: 25px; }
        .logo { max-height: 90px; width: auto; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto; }
        h2 { margin: 5px 0; color: #1a4b8f; font-size: 20px; font-weight: bold; }
        .subtitle { font-size: 14px; color: #666; margin: 0; }

        /* منطقة البحث */
        .search-area { background: #f8fafc; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 25px; border: 1px solid #e2e8f0; }
        input[type="text"] { padding: 12px; width: 60%; border: 1.5px solid #cbd5e1; border-radius: 6px; font-size: 16px; text-align: center; outline: none; }
        .btn-main { background: #1a4b8f; color: white; border: none; padding: 12px 30px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; transition: 0.3s; }
        .btn-main:hover { background: #113361; }

        /* الجدول الرسمي والحدود */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 5px;
            border: 2px solid #222; /* إطار خارجي قوي */
        }
        td { 
            border: 1px solid #222; /* حدود داخلية سوداء واضحة */
            padding: 12px 15px; 
            text-align: right; 
            font-size: 15px; 
            line-height: 1.4;
        }
        .label-cell { background-color: #f1f5f9; font-weight: bold; width: 40%; color: #1e293b; }
        .value-cell { background-color: #ffffff; color: #000; font-weight: 500; }
        
        /* تمييز صف الصافي */
        .net-row { background-color: #dcfce7 !important; font-weight: bold; }
        .net-row td { color: #166534; border-top: 2px solid #222; font-size: 17px; }

        .no-print { display: block; }
        .footer-note { font-size: 11px; color: #94a3b8; text-align: center; margin-top: 25px; border-top: 1px solid #eee; padding-top: 10px; }

        /* وضع الطباعة */
        @media print {
            .no-print, .admin-section { display: none !important; }
            body { background: white; padding: 0; }
            .container { box-shadow: none; border: none; width: 100%; max-width: 100%; padding: 0; }
            table { border: 2px solid #000; }
            td { border: 1px solid #000; }
        }

        /* بوابة الإدارة */
        .admin-section { margin-top: 40px; padding: 15px; background: #fff1f2; border-radius: 8px; border: 1px dashed #fda4af; text-align: center; }
        .admin-section h4 { margin: 0 0 10px 0; color: #be123c; font-size: 13px; }
        .admin-input { padding: 5px; font-size: 12px; border-radius: 4px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/logo_img" alt="جامعة ابن سينا" class="logo" onerror="this.style.display='none'">
            <h2>جامعة ابن سينا للعلوم الطبية والصيدلانية</h2>
            <p class="subtitle">نظام الاستعلام عن رواتب الموظفين (نسخة 2026)</p>
        </div>

        <div class="search-area no-print">
            <form method="POST">
                <input type="text" name="emp_id" placeholder="الرقم الوظيفي" required autofocus>
                <br>
                <button type="submit" class="btn-main">🔍 استخراج البيانات</button>
            </form>
        </div>

        {% if msg %}<p style="text-align:center; color:#e11d48; font-weight:bold;">{{ msg }}</p>{% endif %}

        {% if data %}
        <div id="salary-info">
            <table>
                {% for key, value in data.items() %}
                <tr class="{{ 'net-row' if 'صافي' in key or 'استلام' in key else '' }}">
                    <td class="label-cell">{{ key }}</td>
                    <td class="value-cell">{{ value }}</td>
                </tr>
                {% endfor %}
            </table>
            <button onclick="window.print()" class="btn-main no-print" style="width:100%; background:#475569; margin-top:15px;">🖨️ طباعة كشف الراتب</button>
        </div>
        {% endif %}

        <div class="admin-section no-print">
            <h4>⚙️ لوحة تحكم المالية (تحديث البيانات)</h4>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="password" name="password" placeholder="الرمز السري" class="admin-input" required>
                <input type="file" name="file" accept=".xlsx" class="admin-input" required>
                <button type="submit" style="cursor:pointer; font-size:11px; padding:5px 10px;">رفع الملف</button>
            </form>
        </div>
        
        <p class="footer-note">نظام إلكتروني داخلي - جميع الحقوق محفوظة لجامعة ابن سينا</p>
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
                # تنظيف البيانات لضمان دقة البحث
                df.columns = [str(c).strip() for c in df.columns]
                df['الرقم الوظيفي'] = df['الرقم الوظيفي'].astype(str).str.strip()
                
                res = df[df['الرقم الوظيفي'] == emp_id]
                if not res.empty:
                    # تحويل الصف لقاموس مع الحفاظ على ترتيب الأعمدة (الاسم، الراتب.. إلخ)
                    data = res.iloc[0].to_dict()
                else:
                    msg = "❌ الرقم الوظيفي غير موجود في السجلات."
            except Exception as e:
                msg = "⚠️ خطأ فني في قراءة الملف."
        else:
            msg = "⚠️ قاعدة البيانات غير مرفوعة."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

# دالة ذكية لإظهار الشعار بأي صيغة كانت
@app.route('/logo_img')
def get_logo():
    # يبحث عن ملف باسم logo مع أي صيغة شائعة
    for ext in ['jpg', 'png', 'jpeg', 'JPG', 'PNG']:
        if os.path.exists(f"logo.{ext}"):
            return send_from_directory(os.getcwd(), f"logo.{ext}")
    return "No Logo Found", 404

@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.form.get('password')
    file = request.files.get('file')
    if password == ADMIN_PASSWORD:
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return render_template_string("<h3>✅ تم تحديث الملف بنجاح</h3><a href='/'>عودة للموقع</a>")
    return render_template_string("<h3>❌ فشل التحديث: الرمز خاطئ</h3><a href='/'>محاولة أخرى</a>")

if __name__ == '__main__':
    # Railway يتطلب قراءة المنفذ من البيئة
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
