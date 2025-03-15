import cv2
import os
import numpy as np
from PIL import Image
import csv

def pre_process_check(filepath):
    """
    Perform pre-processing checks on the given image file.
    This function checks the following:
    1. File extension: Ensures the file has a valid image extension (.png, .jpg, .jpeg, .tga).
    2. File size: Ensures the file is not empty and does not exceed 10 MB.
    3. Image dimensions: Ensures the image dimensions are at least 256x256 pixels.
    4. Image readability: Ensures the image can be read successfully.
    Parameters:
    filepath (str): The path to the image file to be checked.
    Raises:
    ValueError: If any of the checks fail, a ValueError is raised with an appropriate error message.
    """
    
    # Check file extension
    valid_extensions = ('.png', '.jpg', '.jpeg', '.tga')
    if not filepath.lower().endswith(valid_extensions):
        raise ValueError("Invalid file extension. Only .png, .jpg, .jpeg, and .tga are allowed.")

    # Check file size
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        raise ValueError("File size is 0. The file may be corrupted.")
    if file_size > 10 * 1024 * 1024:  # 10 MB limit
        raise ValueError("File size is too large. Maximum allowed size is 10 MB.")

    # Check image dimensions
    image = cv2.imread(filepath)
    if image is None:
        raise ValueError("Failed to read the image. The file may be corrupted or not a valid image.")
    height, width = image.shape[:2]
    if height < 256 or width < 256:
        raise ValueError("Image dimensions are too small. Minimum size is 256x256 pixels.")
    
    try:
        img = Image.open(filepath)
        img.verify()  # Verify if the image is corrupted
    except (IOError, SyntaxError) as e:
        raise ValueError(f"Image is corrupted: {e}")

    # Additional checks can be added here
    
    
def load_presets(presets_directory):
    """
    Load all preset CSV files from the specified directory.
    
    Parameters:
        presets_directory (str): Directory containing preset CSV files.

    Returns:
        presets (dict): A dictionary of materials with their properties.
    """
    presets = {}
    
    # Loop through all CSV files in the /presets directory
    for filename in os.listdir(presets_directory):
        if filename.endswith('.csv'):
            with open(os.path.join(presets_directory, filename), mode='r') as file:
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

    return presets

def greyscale_adjust(input_filepath, intensity_factor=1, grey_factor=0.5,material_preset=None):
    """
    Main process fucntion, process an image by normalizing it to grayscale and adjusting its intensity towards 50% greyscale.
    
    Parameters:
        input_filepath (str): Path to the uploaded image file.
        intensity_factor (float): Factor by which the intensity will be adjusted.
        grey_factor (float): Factor to control the shift towards 50% greyscale (0 to 1).
        user_preferences (dict): User preferences for image processing.

    Returns:
        processed_image (numpy.ndarray): The processed image in grayscale with normalized intensity.
    """
    # Read the image as grayscale
    img = cv2.imread(input_filepath, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at {input_filepath} could not be read.")

    # Normalize the image
    img_normalized = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    
    # Adjust intensity by multiplying with intensity_factor
    img_normalized = cv2.convertScaleAbs(img_normalized * intensity_factor)
    
    # Shift towards 50% greyscale
    img_grey_shifted = cv2.addWeighted(img_normalized, 1 - grey_factor, np.full_like(img_normalized, 128), grey_factor, 0)
    
    # for each run of the image processing pipeline, check the user preferences and apply the selected filters    
    

    return img_grey_shifted

def apply_roughness_to_image(image, roughness):
    """
    Apply roughness to the image by adjusting the intensity.
    
    Parameters:
        image (numpy.ndarray): The input image to adjust.
        roughness (int): The roughness value (0 to 100).
    
    Returns:
        adjusted_image (numpy.ndarray): The image with roughness applied.
    """
    # For simplicity, assume roughness directly influences the brightness of the image
    # The higher the roughness, the more diffuse the image becomes.
    roughness_factor = roughness / 100.0  # Convert to a factor between 0 and 1
    adjusted_image = cv2.convertScaleAbs(image * roughness_factor)
    return adjusted_image

def resize_and_crop(image_path, target_size=(512, 512)):
    with Image.open(image_path) as img:
        
        #print("in func target size", target_size)
        
        img = img.convert("RGB")
        width, height = img.size
        
        left = (width - target_size[0]) / 2
        top = (height - target_size[1]) / 2
        right = (width + target_size[0]) / 2
        bottom = (height + target_size[1]) / 2

        img = img.crop((left, top, right, bottom))
        img.save(image_path)
        
def generate_roughness_map(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at {image_path} could not be read.")
    
    # Apply edge detection (e.g., Sobel or Canny)
    edges = cv2.Canny(img, 100, 200)
    
    # Normalize and adjust intensity
    roughness_map = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX)
    roughness_map = cv2.convertScaleAbs(roughness_map * 2.0)  # Adjust intensity
    
    return roughness_map

def generate_normal_map(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at {image_path} could not be read.")
    
    # Generate normal map using Sobel derivatives
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
    
    normal_map = np.dstack((sobel_x, sobel_y, np.ones_like(img)))
    normal_map = cv2.normalize(normal_map, None, 0, 255, cv2.NORM_MINMAX)
    
    return normal_map

def apply_segmentation(image_path):
    """
    Apply AI segmentation to detect multiple materials.
    """
    # Placeholder for segmentation logic
    print("Applying segmentation...")
    return image_path

def detect_material(image_path):
    """
    Detect material using AI or manual selection.
    """
    # Use manually selected material
    #print(f"Using material: {image_path}")
    return image_path

def apply_upscaling(image_path):
    """
    Upscale or downscale the image using AI.
    """
    # Placeholder for upscaling logic
    print("Applying AI upscaling...")
    return image_path

def standardize_pbr(image_path, material_preset = None):
    """
    Standardize PBR values based on the selected preset.
    """
        # If a material preset is provided through the user interface, adjust roughness accordingly
    if material_preset:
        roughness_value = material_preset.get('Roughness', 50)  # Default to 50 if not provided
        img_grey_shifted = apply_roughness_to_image(img_grey_shifted, roughness_value)
    return image_path

def set_texel_density(image_path):
    """
    Set texel density using AI.
    """
    return image_path

def add_grunge(image_path):
    """
    Add grunge map to input texture.
    """
    print("Placeholder feature")
    pass
    process_image = image_path
    return process_image

def remove_artifacts(image_path):
    """
    Remove small artefacts by using AI and smoothing.
    """
    print("Placeholder feature")
    pass
    process_image = image_path
    return process_image

def make_tiling(image_path):
    """
    Make texture tiling for game engines using AI or image processing.
    """
    print("Placeholder feature")
    pass
    process_image = image_path
    return process_image

def force_square(image_path):
    """
    Force resolution to square.
    """
    print("Placeholder feature")
    pass
    process_image = image_path
    return process_image

def generate_metallic(image_path):
    """
    Generate a basic metallic map for the image.
    """
    process_image = image_path
    return process_image

