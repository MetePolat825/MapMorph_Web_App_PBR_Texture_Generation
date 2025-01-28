import os
from flask import Blueprint, render_template, request, redirect, url_for
from app.config import Config

bp = Blueprint('main', __name__)

# Homepage route
@bp.route('/')
def index():
    return render_template('index.html')

# Image upload route
@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the file
            filename = file.filename
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            return redirect(url_for('main.upload'))

    # Pass the 'os' module to the template
    uploaded_files = os.listdir(Config.UPLOAD_FOLDER)
    return render_template('upload.html', uploaded_files=uploaded_files)
