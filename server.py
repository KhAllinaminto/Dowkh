import os
from flask import Flask, request, send_file, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
valid_formats = os.getenv('FORMATS', 'mp4,webm').split(',')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality', 'best')

    if not video_url or not format:
        return jsonify({"error": "الرجاء إدخال رابط الفيديو والتنسيق المطلوب!"}), 400

    if format not in valid_formats:
        return jsonify({"error": f"تنسيق الفيديو غير صالح! يرجى اختيار {', '.join(valid_formats)}"}), 400

    ydl_opts = {
        'format': f'bestvideo[ext={format}]+bestaudio/best' if format == 'mp4' else 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)

        if not os.path.exists(file_path):
            return jsonify({"error": "الملف غير موجود!"}), 404

        response = send_file(file_path, as_attachment=True)
        response.headers['Access-Control-Allow-Origin'] = '*'

        def remove_file():
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {str(e)}")

        response.call_on_close(remove_file)
        return response

    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء التحميل: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)