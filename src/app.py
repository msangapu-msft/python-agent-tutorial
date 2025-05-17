from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os

from whitenoise import WhiteNoise

app = Flask(__name__)

app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

print("Starting Flask app...")

UPLOAD_FOLDER = 'static/uploads'
CONVERTED_FOLDER = 'converted'
THUMBS_FOLDER = 'static/thumbs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(THUMBS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

@app.route('/')
def index():
    # List JPG/JPEG files in uploads/
    jpg_files = sorted([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.jpg', '.jpeg'))])
    return render_template('index.html', files=jpg_files)

@app.route('/images')
def list_images():
    ext = request.args.get('ext', '').lower()
    folder = UPLOAD_FOLDER if ext == 'jpg' else CONVERTED_FOLDER
    images = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
    return '\n'.join(images)

@app.route('/convert', methods=['GET'])
def convert_selected():
    image_names = request.args.get('imgNames', '').strip(',').split(',')
    converted = []

    for name in image_names:
        src_path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.exists(src_path):
            try:
                img = Image.open(src_path)
                # Always convert to PNG format
                img = img.convert("RGB")
                out_name = os.path.splitext(name)[0] + '.png'
                out_path = os.path.join(CONVERTED_FOLDER, out_name)
                img.save(out_path, format='PNG')
                converted.append(out_name)
            except Exception as e:
                print(f"Failed to convert {name}: {e}")

    return jsonify({"converted": converted})

@app.route('/delete', methods=['GET'])
def delete_converted():
    files = os.listdir(CONVERTED_FOLDER)
    for f in files:
        try:
            os.remove(os.path.join(CONVERTED_FOLDER, f))
            # Optionally remove from thumbs if you create thumbs for PNGs
            # os.remove(os.path.join(THUMBS_FOLDER, f))
        except Exception:
            pass
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)