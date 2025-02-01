import os
from flask import Flask, request, send_file
import yt_dlp

app = Flask(__name__)

# استبدال الأسماء القديمة بالأسماء الجديدة
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
valid_formats = os.getenv('FORMATS', 'mp4,webm').split(',')

# إنشاء مجلد التنزيلات إذا لم يكن موجودًا
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality')

    # التحقق من أن المستخدم أدخل رابط وتنسيق
    if not video_url or not format:
        return "الرجاء إدخال رابط الفيديو والتنسيق المطلوب!", 400

    # التحقق من صحة تنسيق الفيديو
    if format not in valid_formats:
        return f"تنسيق الفيديو غير صالح! يرجى اختيار {', '.join(valid_formats)}.", 400

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
        response = send_file(file_path, as_attachment=True)

        # حذف الملف بعد إرساله
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
            return response

        response.call_on_close(remove_file)
        return response

    except Exception as e:
        # إرجاع رسالة الخطأ
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

if __name__ == '__main__':
    # استخدام المنفذ من المتغير البيئي أو 3000 كافتراضي
    port = int(os.getenv('PORT', 3000))
    # تشغيل التطبيق على جميع الواجهات (0.0.0.0)
    app.run(host='0.0.0.0', port=port)