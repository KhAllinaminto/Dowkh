from flask import Flask, request, send_file, Response
from flask_cors import CORS  # استيراد مكتبة CORS
import os
import yt_dlp  # استيراد yt-dlp بدلًا من youtube-dl

# إنشاء تطبيق Flask
app = Flask(__name__)
CORS(app)  # تمكين CORS لجميع المسارات

# مجلد التنزيلات
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# مسار لتحميل الفيديو
@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality')

    # التحقق من أن المستخدم أدخل رابط وتنسيق
    if not video_url or not format:
        return "الرجاء إدخال رابط الفيديو والتنسيق المطلوب!", 400

    # إعداد خيارات yt-dlp
    ydl_opts = {
        'format': f'{format}/{quality}' if format == 'mp4' else 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'restrictfilenames': True,  # تجنب الأحرف غير المسموح بها في أسماء الملفات
        'noplaylist': True,  # تحميل الفيديو فقط وليس القائمة
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج معلومات الفيديو
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        # إرجاع الملف للمستخدم
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        # إرجاع رسالة الخطأ
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

# تشغيل الخادم
if __name__ == '__main__':
    app.run(port=3000)