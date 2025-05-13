# 🎵 YouTube to MP3 Downloader

Tool konversi YouTube ke MP3 berbasis **Flask** dan **TailwindCSS** dengan tampilan clean, progress bar animasi, dan status realtime.

![Preview UI](https://raw.githubusercontent.com/yonaldi1979/ytdownload/main/assets/ui-preview.png)


---

## 🚀 Fitur Utama

- ✅ UI responsif dengan TailwindCSS
- ✅ Background acak tiap refresh
- ✅ Progress bar striping + bubble progress
- ✅ Konversi otomatis ke MP3 (128–320 kbps)
- ✅ Status: Downloading, Converting, Done
- ✅ Tombol download hasil langsung dari browser

---

## 📦 Kebutuhan

- Python 3.10+
- `ffmpeg` terinstal
- `venv` / virtualenv

---

## 🔧 Cara Install & Jalankan

```bash
git clone git@github.com:yonaldi1979/ytdownload.git
cd ytdownload

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Jalankan server
python app.py
