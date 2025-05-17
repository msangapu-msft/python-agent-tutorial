from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
THUMBS_FOLDER = 'static/thumbs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs(THUMBS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

@app.route('/')
def index():
    thumb_files = []
    if os.path.exists(THUMBS_FOLDER):
        thumb_files = sorted([f for f in os.listdir(THUMBS_FOLDER) if f.lower().endswith('.png')])
    return render_template('index.html', files=thumb_files)

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
                out_name = os.path.splitext(name)[0] + '.png'
                out_path = os.path.join(CONVERTED_FOLDER, out_name)
                img.save(out_path)

                img.thumbnail((150, 150))
                img.save(os.path.join(THUMBS_FOLDER, out_name))

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
            os.remove(os.path.join(THUMBS_FOLDER, f))
        except Exception:
            pass
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run(debug=True)
