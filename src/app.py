from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import os
import psutil
import traceback
import sys

from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

sys.stdout.reconfigure(line_buffering=True)
print("Starting Flask app...")

# Config
UPLOAD_FOLDER = 'static/uploads'
THUMBS_FOLDER = 'static/thumbs'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_IMAGES = 12
MAX_FILE_SIZE_MB = 16  # Optional: max 16 MB per file

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(THUMBS_FOLDER, exist_ok=True)

def log_memory_usage(msg=""):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    line = f"[MEMORY] {msg} Memory usage: {mem_mb:.2f} MB\n"
    with open("/home/LogFiles/custom_memlog.txt", "a") as f:
        f.write(line)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    jpg_files = sorted([
        f for f in os.listdir(UPLOAD_FOLDER)
        if allowed_file(f) and f.lower().endswith(('jpg', 'jpeg'))
    ])
    return render_template('index.html', files=jpg_files)

@app.route('/images')
def list_images():
    ext = request.args.get('ext', '').lower()
    folder = UPLOAD_FOLDER if ext == 'jpg' else CONVERTED_FOLDER
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return '', 204
    images = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
    return '\n'.join(images)

@app.route('/convert', methods=['GET'])
def convert_selected():
    log_memory_usage("Before starting conversions")
    image_names_raw = request.args.get('imgNames', '')
    image_names = image_names_raw.strip(',').split(',')

    # Early checks
    if not image_names or (len(image_names) == 1 and not image_names[0]):
        return jsonify({"error": "No images selected."}), 400
    if len(image_names) > MAX_IMAGES:
        return jsonify({"error": f"Too many images selected (limit is {MAX_IMAGES})."}), 400

    converted = []
    errors = {}

    for name in image_names:
        log_memory_usage(f"Before processing {name}")
        name = secure_filename(name.strip())
        if not name or not allowed_file(name):
            msg = f"Skipping invalid file: {name}"
            print("⚠️", msg)
            errors[name] = msg
            continue

        src_path = os.path.join(UPLOAD_FOLDER, name)
        if not os.path.exists(src_path):
            msg = f"File not found: {src_path}"
            print("⚠️", msg)
            errors[name] = msg
            continue

        # File size check
        try:
            file_size_mb = os.path.getsize(src_path) / (1024 * 1024)
            print(f"Processing {name}: {file_size_mb:.2f} MB")
            if file_size_mb > MAX_FILE_SIZE_MB:
                msg = f"File too large ({file_size_mb:.2f} MB > {MAX_FILE_SIZE_MB} MB)"
                print("❌", msg)
                errors[name] = msg
                continue
        except Exception as e:
            errors[name] = f"Could not check file size: {e}"
            continue

        try:
            with Image.open(src_path) as img:
                print(f"{name}: format={img.format}, size={img.size}, mode={img.mode}")
                img = img.convert("RGB")
                out_name = os.path.splitext(name)[0] + '.png'
                out_path = os.path.join(CONVERTED_FOLDER, out_name)
                img.save(out_path, format='PNG')
                converted.append(out_name)
                log_memory_usage(f"After processing {name}")
        except UnidentifiedImageError:
            msg = f"Not a valid image file: {name}"
            print("❌", msg)
            errors[name] = msg
        except Exception as e:
            msg = f"Failed to convert {name}: {e}"
            print("❌", msg)
            errors[name] = msg

    log_memory_usage("After all conversions")

    response = {"converted": converted}
    if errors:
        response["errors"] = errors

    # Optionally, set status code for partial success (207 Multi-Status)
    status = 207 if errors and converted else (400 if errors and not converted else 200)
    return jsonify(response), status

@app.route('/delete', methods=['GET'])
def delete_converted():
    deleted = []
    failed = []
    for f in os.listdir(CONVERTED_FOLDER):
        try:
            os.remove(os.path.join(CONVERTED_FOLDER, f))
            deleted.append(f)
        except Exception as e:
            print(f"⚠️ Failed to delete {f}: {e}")
            failed.append(f)
    return jsonify({"status": "deleted", "deleted": deleted, "failed": failed})

@app.errorhandler(Exception)
def handle_exception(e):
    print("⚠️ Unhandled Exception:", traceback.format_exc())
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
