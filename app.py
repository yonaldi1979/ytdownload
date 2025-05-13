from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import uuid
from threading import Thread
import re
import time

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
download_progress = {}

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def sanitize_filename(name):
    # Hapus karakter ilegal di filename
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_audio(url, quality, task_id):
    download_progress[task_id] = "0.0"

    uid = str(uuid.uuid4())
    temp_output = os.path.join(DOWNLOAD_FOLDER, f"{uid}.%(ext)s")

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent_raw = d.get('_percent_str', '0.0%')
            # Bersihkan karakter ANSI/warna terminal jika ada
            percent_clean = re.sub(r'\x1b\[.*?m', '', percent_raw).strip()
            download_progress[task_id] = percent_clean
        elif d['status'] == 'finished':
            download_progress[task_id] = "90.0"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_output,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'progress_hooks': [progress_hook],
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get('title', f'youtube_audio_{uid}'))
            final_file = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")

            # Cari file MP3 hasil convert
            temp_file = next((f for f in os.listdir(DOWNLOAD_FOLDER)
                              if f.endswith(".mp3") and uid in f), None)
            if temp_file:
                os.rename(os.path.join(DOWNLOAD_FOLDER, temp_file), final_file)
                time.sleep(1)  # delay sebentar untuk antisipasi race condition
                download_progress[task_id] = f"done::{final_file}"
            else:
                download_progress[task_id] = f"error::Gagal menemukan file MP3 hasil convert"
    except Exception as e:
        download_progress[task_id] = f"error::{str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    url = request.form["url"]
    quality = request.form.get("quality", "192")
    task_id = str(uuid.uuid4())

    thread = Thread(target=download_audio, args=(url, quality, task_id))
    thread.start()

    return jsonify({"task_id": task_id})

@app.route("/progress/<task_id>")
def progress(task_id):
    status = download_progress.get(task_id, "unknown")
    if status.startswith("done::"):
        file_path = status.split("::")[1]
        return jsonify({
            "status": "done",
            "file": f"/download/{os.path.basename(file_path)}"
        })
    elif status.startswith("error::"):
        return jsonify({
            "status": "error",
            "message": status.split("::", 1)[1]
        })
    else:
        return jsonify({
            "status": "downloading",
            "progress": status
        })

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=5005)
