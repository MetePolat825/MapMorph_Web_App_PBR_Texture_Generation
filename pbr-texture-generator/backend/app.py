from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import os
import cv2
import zipfile
import shutil
import json  # For saving presets
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from src.image_processing import process_image, resize_and_crop

# initialize flask app from current file
app = Flask(__name__)

# create a folder for uploads and processed images
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Clear the uploads and processed folders on startup to avoid duplication from previous runs.
def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isdir(file_path): # if item is a directory, remove it and its contents
                shutil.rmtree(file_path)
            else:
                os.unlink(file_path) # if item is a file, remove it
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


##################################################################
# Routes for the image processing application
# The routes are defined in the following order:
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

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

# Static route for processed images as a zip file
@app.route('/download/processed.zip')
def download_zip():
    zip_filename = 'mapmorph generated textures.zip'
    zip_filepath = os.path.join(PROCESSED_FOLDER, zip_filename)

    # Remove pre-existing zip if exists
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
    
    # Clear the uploads and processed folders before processing new images
    clear_folder(PROCESSED_FOLDER)
    clear_folder(UPLOAD_FOLDER)
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Check if user is logged in
    #username = request.headers.get('Username')
    #user = User.query.filter_by(username=username).first() if username else None
    #file_limit = 10 if user else 3  # Free users: 3 files, logged-in users: 10 files
    
    file_limit = 10 # Limit the number of files to 10 for now, implement login later

    files = request.files.getlist('file')
    if len(files) > file_limit:
        return jsonify({"error": f"Maximum {file_limit} files allowed"}), 400

    # Process files
    processed_files = []
    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            resize_and_crop(filepath)
            # process_image is the master function that calls all other functions through image_processing.py
            processed_img = process_image(filepath)
            processed_filepath = os.path.join(PROCESSED_FOLDER, file.filename)
            cv2.imwrite(processed_filepath, processed_img)
            processed_files.append(file.filename)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Images processed", "files": processed_files})

if __name__ == '__main__':
    app.run(debug=True)