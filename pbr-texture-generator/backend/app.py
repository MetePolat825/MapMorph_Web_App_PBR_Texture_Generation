import os
import zipfile
import shutil
import json

import cv2

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory

from src.image_processing import load_presets, greyscale_adjust, resize_and_crop, detect_material, apply_upscaling, standardize_pbr, set_texel_density, pre_process_check, force_square, add_grunge, remove_artifacts, make_tiling, convert_image, generate_metallic, generate_normal_map

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
    # files = request.files.getlist('file')
    preferences = json.loads(request.form['preferences'])

    # Load PBR presets from the /presets directory
    pbr_presets_directory = './presets'
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
            pre_process_check(filepath)

            #########################################################################
            # Apply user preferences
            #########################################################################

            # Target resolution, resize the image to fit the new size
            export_resolution = preferences.get('target_export_resolution', "512x512")
            print("preferred export_resolution:", export_resolution)
            width, height = map(int, export_resolution.split('x'))
            resized_cropped_image = resize_and_crop(filepath, target_size=(width, height))

            # base greyscale adjust. change this to work on top of resize, not replace!
            processed_image = greyscale_adjust(resized_cropped_image)

            # Apply AI segmentation if selected
            if preferences.get('use_ai_segmentation', False):
                pass
                print("AI segmentation feature is in development and will be implemented later.")
                # processed_image = apply_segmentation(processed_image)

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
                material_preset = pbr_presets.get(material_preset_name, None)
                processed_image = standardize_pbr(processed_image, material_preset)

            # Set texel density if selected
            if preferences.get('set_texel_ai', False):
                pass
                print("Set Texel Density feature is in development and will be implemented later.")
                texel_value = preferences.get('texel_value', 1.0)
                processed_image = set_texel_density(processed_image, texel_value)

            # Apply post-processing workflow if provided
            # workflow = preferences.get('workflow', None)
            # if workflow:
                # processed_image = apply_post_processing(processed_image, workflow)

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
                processed_image = make_tiling(processed_image)
                print("Made tiling image.")

            # Force square if selected
            if preferences.get('force_square', False):
                print("Force square feature is in development and will be implemented later.")
                pass
                processed_image = force_square(processed_image)
                
            #########################################################################
            # Output Maps
            #########################################################################

            # Generate roughness map if selected
            if preferences.get('generate_roughness', None):
                specular_workflow_preference = preferences.get('specular_workflow', "PBR Rough/Metallic Workflow")
                if specular_workflow_preference == "PBR Rough/Metallic Workflow":
                    print("Using PBR Rough/Metallic Workflow")
                else:
                    print("Using Specular/Glossiness Workflow")
                
            # Generate metallic map if selected
            if preferences.get('generate_metallic', None):
                
                material_preset_name = preferences.get('manual_material_selection', 'Brick')
                material_preset = pbr_presets.get(material_preset_name, {})

                metallic_value = material_preset.get('IsMetallic', 0)  # Default to not metallic if not specified
                
                print("Material preset:", material_preset_name, "IsMetallic:", metallic_value)

                metallic_map = generate_metallic(processed_image,metallic_value)
                
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

            # Generate normal map if selected
            if preferences.get('generate_normal', None):
                
                normal_preset_name = preferences.get('normal_bump_workflow', 'Normal Map')
                
                print("Selected normal map preset:", normal_preset_name)

                normal_map = generate_normal_map(resized_cropped_image, normal_preset_name)
                
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
                
            # export format setup, conversion logic goes here
            export_preference = preferences.get('export_format', "Don't Convert")

            print("Exporting image as", export_preference)
            if not export_preference == "Don't Convert":
                processed_image = convert_image(processed_image, export_preference)
            
            if naming_convention == "Don't Convert":
                processed_filename = os.path.splitext(file.filename)[0] + "_Roughness." + desired_extension
            elif naming_convention == "T_texturename_Roughness":
                processed_filename = "T_" + os.path.splitext(file.filename)[0] + "_Roughness." + desired_extension
            else:
                processed_filename = "T_" + os.path.splitext(file.filename)[0] + "_R." + desired_extension
                
            print("Processed roughness texture saved as", processed_filename)

            #########################################################################
            # Applied user preferences
            #########################################################################

            # Process the image and save it to the processed folder
            processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)
            cv2.imwrite(processed_filepath, processed_image)
            processed_files.append(processed_filename)

        except ValueError as e:
            return jsonify({"Error during main processing loop:": str(e)}), 400
        
    return jsonify({"message": "Images processed", "files": processed_files})


if __name__ == '__main__':
    app.run(debug=True)
