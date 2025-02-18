from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import os
import cv2
import zipfile
import shutil  # For clearing the processed folder
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from src.image_processing import process_image, resize_and_crop  # Importing the process_image function

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Clear the uploads and processed folders on startup
def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

clear_folder(UPLOAD_FOLDER)
clear_folder(PROCESSED_FOLDER)

##################################################################
# Database
##################################################################
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    membership = db.Column(db.String(20), default='free')
    preferences = db.Column(db.JSON, default={})

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create the database
with app.app_context():
    db.create_all()
##################################################################


# Serve the index.html file
@app.route('/')
def home():
    return render_template('index.html')

# Route for the processing page
@app.route('/processing')
def processing():
    return render_template('processing.html')

# Route for the login/signup page
@app.route('/auth')
def auth():
    return render_template('auth.html')

# Route for the help page
@app.route('/help')
def help():
    return render_template('help.html')

# Route for the pricing page
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# Route for the bug report page
@app.route('/bug_report')
def bug_report():
    return render_template('bug_report.html')

# Static route for processed images as a zip file
@app.route('/download/processed.zip')
def download_zip():
    zip_filename = 'processed.zip'
    zip_filepath = os.path.join(PROCESSED_FOLDER, zip_filename)

    # Clear the zip file if it already exists
    if os.path.exists(zip_filepath):
        os.remove(zip_filepath)

    # Create a new zip file with the processed files
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for filename in os.listdir(PROCESSED_FOLDER):
            file_path = os.path.join(PROCESSED_FOLDER, filename)
            if os.path.isfile(file_path) and filename != zip_filename:  # Avoid adding the zip file itself
                zipf.write(file_path, os.path.basename(file_path))

    # Send the zip file to the user's download folder
    return send_file(zip_filepath, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Check if user is logged in
    username = request.headers.get('Username')
    user = User.query.filter_by(username=username).first() if username else None
    file_limit = 10 if user else 3  # Free users: 3 files, logged-in users: 10 files

    files = request.files.getlist('file')
    if len(files) > file_limit:
        return jsonify({"error": f"Maximum {file_limit} files allowed"}), 400

    # Process files (existing logic)
    processed_files = []
    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            resize_and_crop(filepath)
            processed_img = process_image(filepath)
            processed_filepath = os.path.join(PROCESSED_FOLDER, file.filename)
            cv2.imwrite(processed_filepath, processed_img)
            processed_files.append(file.filename)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Images processed", "files": processed_files})

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)


##################################################################
# Authentication routes
##################################################################

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"message": "Logged in successfully", "username": user.username, "membership": user.membership})
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created successfully", "username": user.username, "membership": user.membership})

if __name__ == '__main__':
    app.run(debug=True)