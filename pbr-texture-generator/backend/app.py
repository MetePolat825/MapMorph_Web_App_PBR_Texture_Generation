import os
import zipfile
import shutil
import json  # For saving presets
from datetime import datetime, timedelta # for token reset logic

import cv2

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory, redirect, request, flash, session, url_for

from src.image_processing import load_presets,greyscale_adjust, resize_and_crop,apply_segmentation, detect_material, apply_upscaling, standardize_pbr, set_texel_density, pre_process_check, generate_normal_map, force_square, add_grunge, remove_artifacts,make_tiling,generate_metallic

# initialize flask app from current file
app = Flask(__name__)
#app.config['SECRET_KEY'] = '0123456789'

##################################################################
# Image processing routes
# The following routes are used to process images uploaded by the user.
##################################################################

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
    return render_template("auth.html")

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
    zip_filename = 'MyTextures.zip'
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

    # Extract files and preferences from the request
    files = request.files.getlist('file')
    preferences = json.loads(request.form['preferences'])
    
    # Load PBR presets from the /presets directory
    presets_directory = './presets'
    presets = load_presets(presets_directory)

    # Log preferences for debugging
    print("User Preferences:", preferences)

    # Process files
    processed_files = []
    for file in request.files.getlist('file'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            # Pre-process check, file size, file corruption, extension etc.
            pre_process_check(filepath)
            
            #########################################################################
            # Apply user preferences
            #########################################################################
   
            # Target resolution, resize and crop the image
            export_resolution = preferences.get('target_export_resolution', "512x512")
            print("preferred export_resolution",export_resolution)
            width, height = map(int, export_resolution.split('x'))
            resize_and_crop(filepath, target_size=(width, height))

            # base greyscale adjust
            processed_image = greyscale_adjust(filepath)
            
            # Apply AI segmentation if selected
            if preferences.get('use_ai_segmentation', False):
                pass
                print("AI segmentation feature is in development and will be implemented later.")
                #processed_image = apply_segmentation(processed_image)

            # Apply manual material selection if provided
            manual_material = preferences.get('manual_material_selection', None)
            if manual_material:
                processed_image = detect_material(processed_image)
            else:
                print("Error, no material selected.")

            # Apply AI upscaling if selected
            if preferences.get('apply_ai_upscale', False):
                pass
                print("AI Upscaling feature is in development and will be implemented later.")
                processed_image = apply_upscaling(processed_image)

            # Standardize PBR if selected
            if preferences.get('pbr_standardize', False):
                # Apply user preferences PBR material preset to image given dropdown selection
                material_preset_name = preferences.get('material_type', 'Brick')  # Default to brick material
                material_preset = presets.get(material_preset_name, None)
                processed_image = standardize_pbr(processed_image, material_preset)

            # Set texel density if selected
            if preferences.get('set_texel_ai', False):
                pass
                print("Set Texel Density feature is in development and will be implemented later.")
                texel_value = preferences.get('texel_value', 1.0)
                processed_image = set_texel_density(processed_image, texel_value)

            # Apply post-processing workflow if provided
            #workflow = preferences.get('workflow', None)
            #if workflow:
                #processed_image = apply_post_processing(processed_image, workflow)

            # Generate normal/bump map
            normal_bump = preferences.get('normal_bump', None)
            if normal_bump:
                pass
                print("Nomral map generation feature is in development and will be implemented later.")
                #processed_image = generate_normal_map(processed_image)

            # Generate metallic map if selected
            #generate_metallic = preferences.get('generate_metallic', None)
            #if generate_metallic:
                #print("This feature is in development and will be implemented later.")
                #pass

            # Add grunge if selected
            if preferences.get('add_grunge', False):
                print("Add grunge featur    e is in development and will be implemented later.")
                pass
                processed_image = add_grunge(processed_image)

            # Remove artefacts if selected
            if preferences.get('remove_artifacts', False):
                print("Remove artefacts feature is in development and will be implemented later.")
                pass
                processed_image = remove_artifacts(processed_image)

            # Make tilig material tiling if selected
            if preferences.get('make_tiling', False):
                print("Make tiling feature is in development and will be implemented later.")
                pass
                processed_image = make_tiling(processed_image)

            # Force square if selected
            if preferences.get('force_square', False):
                print("Force square feature is in development and will be implemented later.")
                pass
                processed_image = force_square(processed_image)
                
            # export format setup, conversion logic goes here   
            #if preferences.get('export_format')
            
            #########################################################################
            # Applied user preferences
            #########################################################################

            # Process the image and save it to the processed folder
            processed_filepath = os.path.join(PROCESSED_FOLDER, file.filename)
            cv2.imwrite(processed_filepath, processed_image)
            processed_files.append(file.filename)
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Images processed", "files": processed_files})

if __name__ == '__main__':
    app.run(debug=True)