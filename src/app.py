import os, sys, traceback, psutil, gc
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from whitenoise import WhiteNoise

# Config
UPLOAD_FOLDER = 'static/uploads'
THUMBS_FOLDER = 'static/thumbs'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_IMAGES = 12
MAX_FILE_SIZE_MB = 16
ENABLE_LOGGING = os.environ.get("ENABLE_LOGGING", "").lower() in ("1", "true", "yes")

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
sys.stdout.reconfigure(line_buffering=True)

if ENABLE_LOGGING: print("Starting Flask app...")
for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER, THUMBS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def print_log(*args): 
    if ENABLE_LOGGING: print(*args)

def allowed_file(name): 
    return '.' in name and name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_memory(msg=""):
    if not ENABLE_LOGGING: return
    p, v = psutil.Process(os.getpid()), psutil.virtual_memory()
    line = (f"[MEMORY] {msg} | App Memory: {p.memory_info().rss/1024/1024:.2f} MB | "
            f"System: {v.total/1024/1024:.2f} MB | Free: {v.available/1024/1024:.2f} MB | Usage: {v.percent}%\n")
    try:
        with open("/home/LogFiles/custom_memlog.txt", "a") as f:
            f.write(line); f.flush()
    except Exception as e:
        print_log(f"Could not write to memory log: {e}")

@app.route('/')
def index():
    return render_template('index.html', files=get_image_list(UPLOAD_FOLDER, 'jpg'))

@app.route('/images')
def list_images():
    ext = request.args.get('ext', '').lower()
    folder = UPLOAD_FOLDER if ext == 'jpg' else CONVERTED_FOLDER
    if not os.path.exists(folder): return '', 204
    return '\n'.join(get_image_list(folder, ext))

def get_image_list(folder, ext):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(ext)])

@app.route('/convert')
def convert_selected():
    log_memory("Before conversions")
    raw = request.args.get('imgNames', '')
    names = raw.strip(',').split(',')
    if not names or (len(names) == 1 and not names[0]):
        return jsonify({"error": "No images selected."}), 400
    if len(names) > MAX_IMAGES:
        return jsonify({"error": f"Too many images (limit {MAX_IMAGES})"}), 400

    converted, errors = [], {}
    for name in names:
        log_memory(f"Before {name}")
        name = secure_filename(name.strip())
        if not name or not allowed_file(name):
            errors[name] = f"Skipping invalid file: {name}"; print_log(errors[name]); continue
        src = os.path.join(UPLOAD_FOLDER, name)
        if not os.path.exists(src):
            errors[name] = f"File not found: {src}"; print_log(errors[name]); continue
        try:
            if os.path.getsize(src)/(1024*1024) > MAX_FILE_SIZE_MB:
                errors[name] = f"{name} too large"; print_log(errors[name]); continue
        except Exception as e:
            errors[name] = f"Size check failed: {e}"; continue
        try:
            with Image.open(src) as img:
                print_log(f"{name}: format={img.format}, size={img.size}, mode={img.mode}")

                # Optional: downsize large images to reduce memory footprint
                if img.width > 1920 or img.height > 1920:
                    img.thumbnail((1920, 1920))  # Maintains aspect ratio

                img = img.convert("RGB")  # Conversion can still use memory
                out_name = os.path.splitext(name)[0] + '.png'
                out_path = os.path.join(CONVERTED_FOLDER, out_name)

                # Save directly to disk to reduce in-memory footprint
                with open(out_path, 'wb') as f:
                    img.save(f, format='PNG')

                converted.append(os.path.basename(out_path))

            # Free memory and delete source file
            os.remove(src)
            del img
            gc.collect()
            print_log(f"Converted and deleted {name}")
        except UnidentifiedImageError:
            errors[name] = f"{name} is not a valid image"
        except Exception as e:
            errors[name] = f"Failed to convert {name}: {e}"
        log_memory(f"After {name}")

    log_memory("After all")
    resp = {"converted": converted}
    if errors: resp["errors"] = errors
    return jsonify(resp), 207 if errors and converted else (400 if errors else 200)

@app.route('/delete')
def delete_converted():
    deleted, failed = [], []
    for f in os.listdir(CONVERTED_FOLDER):
        try: os.remove(os.path.join(CONVERTED_FOLDER, f)); deleted.append(f)
        except Exception as e: print_log(f"Failed to delete {f}: {e}"); failed.append(f)
    return jsonify({"status": "deleted", "deleted": deleted, "failed": failed})

@app.errorhandler(Exception)
def handle_exception(e):
    print_log("Unhandled Exception:", traceback.format_exc())
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
