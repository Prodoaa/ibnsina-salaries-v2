from flask import Flask, request, render_template_string, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# --- الإعدادات ---
ADMIN_PASSWORD = "UISM_2026_ADMIN" 
LOCAL_FILE = "salaries.xlsx"
# تأكد من تسمية صورة الشعار في المجلد بـ logo.jpg أو logo.png
LOGO_FILENAME = "logo.jpg" 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الرواتب | جامعة ابن سينا</title>
    <style>
        body { 
            font-family: 'Arial', sans-serif; 
            background-color: #f4f7f6; 
            margin: 0; 
            padding: 20px; 
            color: #333;
        }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        
        /* الشعار والترويسة */
        .header { text-align: center; border-bottom: 2px solid #1a4b8f; padding-bottom: 15px; margin-bottom: 20px; }
        .logo { max-height: 100px; width: auto; margin-bottom: 10px; }
        h2 { margin: 0; color: #1a4b8f; font-size: 20px; }
        
        .search-area { background: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; border: 1px solid #ddd; }
        input[type="text"] { padding: 10px; width: 250px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; text-align: center; }
        .btn { background: #1a4b8f; color: white; border: none; padding: 10px 25px; border-radius: 4px; cursor: pointer; font-weight: bold; }

        /* الجدول الرسمي المنسق */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 10px;
            border: 2px solid #333; /* حدود خارجية واضحة */
        }
        th, td { 
            border: 1px solid #333; /* حدود داخلية واضحة */
            padding: 10px 15px; 
            text-align: right; 
            font-size: 15px; 
        }
        .label-cell { background-color: #eee; font-weight: bold; width: 40%; }
        .value-cell { background-color: #fff; }
        
        /* سطر الصافي */
        .net-row { background-color: #e8f5e9 !important; font-weight: bold; }
        .net-row td { color: #2e7d32; border-top: 2px solid #333; }

        .no-print { display: block; margin-top: 15px; }
        .footer-note { font-size: 11px; color: #777; text-align: center; margin-top: 20px; }

        @media print {
            .no-print { display: none; }
            body { background: white; padding: 0; }
            .container { box-shadow: none; border: none; width: 100%; max-width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/logo_img" alt="جامعة ابن سينا" class="logo" onerror="this.style.display='none'">
            <h2>جامعة ابن سينا للعلوم الطبية والصيدلانية</h2>
            <p style="margin:5px 0; font-size:14px;">كشف راتب الموظف الإلكتروني</p>
        </div>

        <div class="search-area no-print">
            <form method="POST">
                <input type="text" name="emp_id" placeholder="الرقم الوظيفي" required>
                <button type="submit" class="btn">استعلام</button>
            </form>
        </div>

        {% if msg %}<p style="text-align:center; color:red;">{{ msg }}</p>{% endif %}

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
            <button onclick="window.print()" class="btn no-print" style="width:100%; background:#444; margin-top:10px;">طباعة الكشف</button>
        </div>
        {% endif %}

        <div class="admin-area no-print" style="margin-top:40px; font-size:12px; border-top:1px dashed #ccc; padding-top:10px;">
            <form method="POST" action="/upload" enctype="multipart/form-data">
                كلمة السر: <input type="password" name="password" style="padding:3px;">
                ملف Excel: <input type="file" name="file" accept=".xlsx">
                <button type="submit">تحديث</button>
            </form>
        </div>
        
        <p class="footer-note">هذا الكشف صادر عن النظام الإلكتروني لجامعة ابن سينا 2026</p>
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
                    # تحويل الصف إلى قاموس لعرضه في الجدول بالكامل
                    data = res.iloc[0].to_dict()
                else:
                    msg = "الرقم الوظيفي غير موجود."
            except:
                msg = "حدث خطأ في قراءة ملف البيانات."
        else:
            msg = "لم يتم رفع قاعدة البيانات."
    return render_template_string(HTML_TEMPLATE, msg=msg, data=data)

# دالة مخصصة لخدمة صورة الشعار
@app.route('/logo_img')
def get_logo():
    # يبحث عن الملف بأي صيغة شائعة
    for ext in ['jpg', 'png', 'jpeg']:
        if os.path.exists(f"logo.{ext}"):
            return send_from_directory(os.getcwd(), f"logo.{ext}")
    return "No logo", 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.form.get('password') == ADMIN_PASSWORD:
        file = request.files.get('file')
        if file and file.filename.endswith('.xlsx'):
            file.save(LOCAL_FILE)
            return "تم التحديث بنجاح. <a href='/'>عودة</a>"
    return "فشل التحديث. <a href='/'>عودة</a>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
