import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

# تفعيل CORS للسماح بجميع الطلبات
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
valid_formats = os.getenv('FORMATS', 'mp4,webm').split(',')

# إنشاء مجلد التنزيلات إذا لم يكن موجودًا
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return "مرحبًا! تطبيق تحميل الفيديوهات يعمل."

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality')

    if not video_url or not format:
        return jsonify({"error": "الرجاء إدخال رابط الفيديو والتنسيق المطلوب!"}), 400

    if format not in valid_formats:
        return jsonify({"error": f"تنسيق الفيديو غير صالح! يرجى اختيار {', '.join(valid_formats)}"}), 400

    ydl_opts = {
        'format': f'{format}/{quality}' if format == 'mp4' else 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        response = send_file(file_path, as_attachment=True)
        
        # السماح بالطلبات من أي مصدر (CORS)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
            return response

        response.call_on_close(remove_file)
        return response

    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء التحميل: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
