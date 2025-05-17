from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import os

from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

print("Starting Flask app...")

UPLOAD_FOLDER = 'static/uploads'
THUMBS_FOLDER = 'static/thumbs'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_IMAGES = 8  # To prevent abuse or memory overload

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(THUMBS_FOLDER, exist_ok=True)

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
        return '', 204
    images = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
    return '\n'.join(images)

@app.route('/convert', methods=['GET'])
def convert_selected():
    image_names_raw = request.args.get('imgNames', '')
    image_names = image_names_raw.strip(',').split(',')

    if not image_names or len(image_names) > MAX_IMAGES:
        return jsonify({"error": "Too many images or none selected."}), 400

    converted = []

    for name in image_names:
        name = secure_filename(name.strip())
        if not name or not allowed_file(name):
            print(f"⚠️ Skipping invalid file: {name}")
            continue

        src_path = os.path.join(UPLOAD_FOLDER, name)
        if not os.path.exists(src_path):
            print(f"⚠️ File not found: {src_path}")
            continue

        try:
            with Image.open(src_path) as img:
                img = img.convert("RGB")
                out_name = os.path.splitext(name)[0] + '.png'
                out_path = os.path.join(CONVERTED_FOLDER, out_name)
                img.save(out_path, format='PNG')
                converted.append(out_name)
        except UnidentifiedImageError:
            print(f"❌ Not a valid image file: {name}")
        except Exception as e:
            print(f"❌ Failed to convert {name}: {e}")

    return jsonify({"converted": converted})

@app.route('/delete', methods=['GET'])
def delete_converted():
        try:
            os.remove(os.path.join(CONVERTED_FOLDER, f))
        except Exception as e:
            print(f"⚠️ Failed to delete {f}: {e}")
        return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
