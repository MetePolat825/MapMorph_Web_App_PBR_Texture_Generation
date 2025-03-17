import os
import zipfile
import shutil
import json
import csv

import cv2

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory

from src.image_processing import ImageProcessor

app = Flask(__name__)

# create a folder for uploads and processed images
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)


# Clear the uploads and processed folders on startup to avoid duplication from previous runs.
def clear_folder(folder: str) -> None:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isdir(file_path):  # if item is a directory, remove it and its contents
                shutil.rmtree(file_path)
            else:
                os.unlink(file_path)  # if item is a file, remove it
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


@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(os.path.abspath(PROCESSED_FOLDER), filename)


# Static route for processed images as a zip file
@app.route('/download/processed.zip')
def download_zip():
    zip_filename = 'MyTextures.zip'
    zip_filepath = os.path.join(PROCESSED_FOLDER, zip_filename)

    # Debugging: Check if the processed folder exists
    if not os.path.exists(PROCESSED_FOLDER):
        return jsonify({"error": "Processed folder not found"}), 500

    # Remove pre-existing zip file if it exists
    if os.path.exists(zip_filepath):
        os.remove(zip_filepath)

    # Check if there are any files to add to the zip
    files_to_zip = [f for f in os.listdir(PROCESSED_FOLDER) if os.path.isfile(os.path.join(PROCESSED_FOLDER, f)) and f != zip_filename]

    if not files_to_zip:
        return jsonify({"error": "No processed files found to zip"}), 400

    # Create a new zip file with the processed files
    try:
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for filename in files_to_zip:
                file_path = os.path.join(PROCESSED_FOLDER, filename)
                zipf.write(file_path, os.path.basename(file_path))

        # Debugging: Check if the zip file was created
        if not os.path.exists(zip_filepath):
            return jsonify({"error": "Failed to create ZIP file"}), 500

    except Exception as e:
        return jsonify({"error": f"Error creating ZIP: {str(e)}"}), 500

    # Send the zip file
    return send_file(os.path.abspath(zip_filepath), as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload_image():
    # Clear the uploads and processed folders before processing new images
    clear_folder(PROCESSED_FOLDER)
    clear_folder(UPLOAD_FOLDER)

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Extract files and preferences from the request
    # files = request.files.getlist('file')
    preferences = json.loads(request.form['preferences'])

    # Load PBR presets from the /presets directory
    pbr_presets_directory = 'presets'  # Use relative path
    pbr_presets = load_presets(pbr_presets_directory)
    
    naming_convention = preferences.get("naming_convention","Don't Convert")
    if naming_convention == "Don't Convert":
        naming_convention = ""
    
    desired_extension = preferences.get("export_format","Don't Convert")
        
    print("Desired extension:", desired_extension)

    # Log preferences for debugging
    print("User Preferences:", preferences)

    processed_files = []
    for file in request.files.getlist('file'):
        
        if desired_extension == "Don't Convert":
            desired_extension = file.filename.split('.')[-1]  # Default to the original file extension
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            # Pre-process check, file size, file corruption, extension etc.
            ImageProcessor.pre_process_check(filepath)

            #########################################################################
            # Apply user preferences
            #########################################################################

            # Target resolution, resize the image to fit the new size
            export_resolution = preferences.get('target_export_resolution', "512x512")
            width, height = map(int, export_resolution.split('x'))
            resized_cropped_image = ImageProcessor.resize_and_crop(filepath, target_size=(width, height))

            # base greyscale adjust. change this to work on top of resize, not replace!
            processed_image = ImageProcessor.greyscale_adjust(resized_cropped_image)

            # Apply AI segmentation if selected
            if preferences.get('use_ai_segmentation', False):
                pass
                print("AI segmentation feature is in development and will be implemented later.")
                # processed_image = apply_segmentation(processed_image)

            # Apply manual material selection if provided
            manual_material = preferences.get('manual_material_selection', None)
            if manual_material:
                processed_image = ImageProcessor.detect_material(processed_image)
            else:
                print("Error, no material selected.")

            # Apply AI upscaling if selected
            if preferences.get('apply_ai_upscale', False):
                pass
                print("AI Upscaling feature is in development and will be implemented later.")
                processed_image = ImageProcessor.apply_upscaling(processed_image)

            # Standardize PBR if selected
            if preferences.get('pbr_standardize', False):
                # Apply user preferences PBR material preset to image given dropdown selection
                material_preset_name = preferences.get('material_type', 'Brick')  # Default to brick material
                material_preset = pbr_presets.get(material_preset_name, None)
                processed_image = ImageProcessor.standardize_pbr(processed_image, material_preset)

            # Set texel density if selected
            if preferences.get('set_texel_ai', False):
                pass
                print("Set Texel Density feature is in development and will be implemented later.")
                texel_value = preferences.get('texel_value', 1.0)
                processed_image = ImageProcessor.set_texel_density(processed_image, texel_value)

            # Add grunge if selected
            if preferences.get('add_grunge', False):
                print("Add grunge featur    e is in development and will be implemented later.")
                pass
                processed_image = ImageProcessor.add_grunge(processed_image)

            # Remove artefacts if selected
            if preferences.get('remove_artifacts', False):
                print("Remove artefacts feature is in development and will be implemented later.")
                pass
                processed_image = ImageProcessor.remove_artifacts(processed_image)

            # Make tilig material tiling if selected
            if preferences.get('make_tiling', False):
                processed_image = ImageProcessor.make_tiling(processed_image)
                print("Made tiling image.")

            # Force square if selected
            if preferences.get('force_square', False):
                print("Force square feature is in development and will be implemented later.")
                pass
                processed_image = ImageProcessor.force_square(processed_image)
                
            #########################################################################
            # Output Maps
            #########################################################################

            # export format setup, conversion logic goes here
            export_preference = preferences.get('export_format', "Don't Convert")
            if not export_preference == "Don't Convert":
                print("Exporting image as", export_preference)
                processed_image = ImageProcessor.convert_image_format(processed_image, export_preference)

            # Generate roughness map if selected
            if preferences.get('generate_roughness', None):
                
                specular_workflow_preference = preferences.get('specular_workflow', "PBR Rough/Metallic Workflow")
                
                if specular_workflow_preference == "PBR Rough/Metallic Workflow":
                    print("Using PBR Rough/Metallic Workflow")
 
                    if naming_convention == "Don't Convert":
                        processed_filename = os.path.splitext(file.filename)[0] + "_Roughness." + desired_extension
                    elif naming_convention == "T_texturename_Roughness":
                        processed_filename = "T_" + os.path.splitext(file.filename)[0] + "_Roughness." + desired_extension
                    else:
                        processed_filename = "T_" + os.path.splitext(file.filename)[0] + "_R." + desired_extension
                        
                    # Process the image and save it to the processed folder
                    processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)
                    cv2.imwrite(processed_filepath, processed_image)
                    processed_files.append(processed_filename)
                    
                    print("Processed roughness texture saved as", processed_filename)
                    
                else:
                    print("Using Specular/Glossiness Workflow has not yet been implemented, please select PBR Rough/Metallic Workflow.")
                    return jsonify({"Error": "Specular/Glossiness Workflow has not yet been implemented, please select PBR Rough/Metallic Workflow."}), 400

            # Generate normal map if selected
            if preferences.get('generate_normal', None):
                
                normal_preset_name = preferences.get('normal_bump_workflow', 'Normal Map')
                
                print("Selected normal map preset:", normal_preset_name)

                normal_map = ImageProcessor.generate_normal_map(resized_cropped_image, normal_preset_name)
                
                if naming_convention == "Don't Convert":
                    normal_filename = os.path.splitext(file.filename)[0] + "_Normal." + desired_extension
                elif naming_convention == "T_texturename_Roughness":
                    normal_filename = "T_" + os.path.splitext(file.filename)[0] + "_Normal." + desired_extension
                else:
                    normal_filename = "T_" + os.path.splitext(file.filename)[0] + "_N." + desired_extension
                
                # Export the Normal/Bump map
                normal_filepath = os.path.join(PROCESSED_FOLDER, normal_filename)
                cv2.imwrite(normal_filepath, normal_map)
                print("Normal map saved as", normal_filename)
                processed_files.append(normal_filename)  # add here for frontend visualization
                
            # Generate metallic map if selected
            if preferences.get('generate_metallic', None):
                
                material_preset_name = preferences.get('manual_material_selection', 'Brick')
                material_preset = pbr_presets.get(material_preset_name, {})

                metallic_value = material_preset.get('IsMetallic', 0)  # Default to not metallic if not specified
                
                print("Material preset:", material_preset_name, "IsMetallic:", metallic_value)

                metallic_map = ImageProcessor.generate_metallic(processed_image,metallic_value)
                
                if naming_convention == "Don't Convert":
                    metallic_filename = os.path.splitext(file.filename)[0] + "_Metallic." + desired_extension
                elif naming_convention == "T_texturename_Roughness":
                    metallic_filename = "T_" + os.path.splitext(file.filename)[0] + "_Metallic." + desired_extension
                else:
                    metallic_filename = "T_" + os.path.splitext(file.filename)[0] + "_M." + desired_extension
                
                # Export the metallic map
                metallic_filepath = os.path.join(PROCESSED_FOLDER, metallic_filename)
                cv2.imwrite(metallic_filepath, metallic_map)
                print("Metallic map saved as", metallic_filename)
                processed_files.append(metallic_filename)  # add here for frontend visualization

        except ValueError as e:
            return jsonify({"Error during main processing loop:": str(e)}), 400
        
    return jsonify({"message": "Images processed", "files": processed_files})


def load_presets(presets_directory:str) -> dict:
    """
    Load all preset CSV files from the specified directory.

    Parameters:
        presets_directory (str): Directory containing preset CSV files.

    Returns:
        presets (dict): A dictionary of materials with their properties.
    """
    presets = {}
    
    # Use the absolute path based on the current working directory
    absolute_presets_directory = os.path.join(os.path.dirname(__file__), presets_directory)

    # Loop through all CSV files in the /presets directory
    for filename in os.listdir(absolute_presets_directory):
        if filename.endswith('.csv'):
            with open(os.path.join(absolute_presets_directory, filename), mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    material_name = row["Material"]
                    base_color = row["BaseColor"]
                    roughness = int(row["Roughness"])
                    is_metallic = int(row["IsMetallic"])

                    presets[material_name] = {
                        "BaseColor": base_color,
                        "Roughness": roughness,
                        "IsMetallic": is_metallic
                    }
    print("Presets loaded successfully from CSV files.", absolute_presets_directory)

    return presets


if __name__ == '__main__':
    app.run(debug=True)
