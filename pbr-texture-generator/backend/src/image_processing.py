import cv2
import os
import numpy as np
from PIL import Image
import csv
import io


def pre_process_check(filepath:str) -> None:
    """
    Perform pre-processing checks on the given image file.
    This function checks the following:
    1. File extension: Ensures the file has a valid image extension (.png, .jpg, .jpeg, .bmp).
    2. File size: Ensures the file is not empty and does not exceed 10 MB.
    3. Image dimensions: Ensures the image dimensions are at least 256x256 pixels.
    4. Image readability: Ensures the image can be read successfully.
    Parameters:
    filepath (str): The path to the image file to be checked.
    Raises:
    ValueError: If any of the checks fail, a ValueError is raised with an appropriate error message.
    """

    # Check file extension
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    if not filepath.lower().endswith(valid_extensions):
        raise ValueError("Invalid file extension. Only .png, .jpg, .jpeg, and .bmp are allowed.")

    # Check if the image has 3 channels (RGB)
    image = cv2.imread(filepath)
    if image is None:
        raise ValueError("Failed to read the image. The file may be corrupted or not a valid image.")
    if image.shape[2] != 3:
        raise ValueError("Image does not have 3 channels (RGB).")
    
    # Check file size
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        raise ValueError("File size is 0. The file may be corrupted.")
    if file_size > 15 * 1024 * 1024:  # 15 MB limit
        raise ValueError("File size is too large. Maximum allowed size is 15 MB.")

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


def load_presets(presets_directory:str) -> dict:
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


def greyscale_adjust(img:np.ndarray, intensity_factor:float = 1.0, grey_factor:float = 0.5) -> np.ndarray:
    """
    Main process fucntion, process an image by normalizing it to grayscale and adjusting its intensity towards 50% greyscale.

    Parameters:
        input_filepath (str): Path to the uploaded image file.
        intensity_factor (float): Factor by which the intensity will be adjusted. 0 means black image, 1 means no change, 2 means double intensity.
        grey_factor (float): Factor to control the shift towards 50% greyscale (0 to 1).

    Returns:
        processed_image (numpy.ndarray): The processed image in grayscale with normalized intensity.
    """

    # Normalize the image
    img_normalized = cv2.normalize(img.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Adjust intensity by multiplying with intensity_factor
    img_normalized = cv2.convertScaleAbs(img_normalized * intensity_factor)

    # Shift towards 50% greyscale to get rid of extreme value variations
    img_grey_shifted = cv2.addWeighted(img_normalized, 1 - grey_factor, np.full_like(img_normalized, 128), grey_factor, 0)

    # for each run of the image processing pipeline, check the user preferences and apply the selected filters
    return img_grey_shifted


def standardize_pbr(image: np.ndarray, material_preset=None) -> np.ndarray:
    """
    Standardize PBR values based on the selected preset.
    """
    # If a material preset is provided through the user interface, adjust roughness accordingly
    if material_preset:
        roughness_value = material_preset.get('Roughness', 50)  # Default to 50 if not provided
        print(material_preset, "Debug: Roughness value from preset:", roughness_value)
        img_grey_shifted = apply_roughness_to_image(image, roughness_value)
    return img_grey_shifted


def apply_roughness_to_image(image: np.ndarray, roughness:int = 50) -> np.ndarray:
    """
    Apply roughness to the image by adjusting the intensity.
    This function is intended to be used with the standardized PBR values from the material presets.

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


def resize_and_crop(image_path:str, target_size=(512, 512)) -> np.ndarray:
    """
    Resize and crop the image to the target size and return as a numpy array.
    """
    
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        width, height = img.size

        left = (width - target_size[0]) / 2
        top = (height - target_size[1]) / 2
        right = (width + target_size[0]) / 2
        bottom = (height + target_size[1]) / 2

        cropped_img = img.crop((left, top, right, bottom))
        resized_img = cropped_img.resize(target_size, Image.Resampling.LANCZOS)

        return np.array(resized_img)


def generate_normal_map(image: np.ndarray, normal_configuration:str) -> np.ndarray:
    """Generate a normal map from the input image using the Sobel operator.
    The normal map is a 3-channel image where the first two channels represent the x and y gradients, and the third channel represents the depth.
    
    Args:
        image (np.ndarray): Input image to generate the normal map from. This image should be in RGB format.
        normal_configuration (str): Configuration for generating the normal map.
            "Normal Map" or "Bump Map" (legacy method) selections available.
    
    Returns:
        np.ndarray: Returns the generated normal map as a np.ndarray image.
    """
    
    # Convert image to grayscale (luminance) to simplify the process of gradient calculation
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Sobel operator to calculate gradients in X and Y direction
    grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

    # Normalize gradients to the range [0, 255]
    grad_x = cv2.normalize(grad_x, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    grad_y = cv2.normalize(grad_y, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # The Z component in a normal map is typically the constant (usually 1)
    # Normalize Z to 127 (midpoint of 0 to 255 range, representing neutral depth)
    grad_z = np.full_like(grad_x, 127, dtype=np.uint8)

    # Stack the gradients into a 3-channel image (Normal Map)
    normal_map = np.dstack((grad_x.astype(np.uint8), grad_y.astype(np.uint8), grad_z))

    # Optionally apply different configurations for bump maps or normal maps
    if normal_configuration == "Bump Map":
        # In bump maps, the normal vectors can have different interpretations
        gray_normal_map = cv2.cvtColor(normal_map, cv2.COLOR_BGR2GRAY)

        # Optionally apply custom scaling for bump map visualization
        normal_map = cv2.applyColorMap(gray_normal_map, cv2.COLORMAP_JET)

    return normal_map


def apply_segmentation(image: np.ndarray) -> np.ndarray:
    """
    Apply AI segmentation to detect multiple materials.
    """
    # Placeholder for segmentation logic
    print("Segmentation is still under development and has not yet been implemented...")
    return image


def detect_material(image: np.ndarray) -> np.ndarray:
    """
    Detect material using AI or manual selection.
    """
    # Use manually selected material
    detected_material_image = image
    
    return detected_material_image


def apply_upscaling(image: np.ndarray) -> np.ndarray:
    """
    Upscale or downscale the image using AI.
    """
    # Placeholder for upscaling logic
    print("AI upscaling is still under development and has not yet been implemented..")
    upscaled_image = image
    return upscaled_image


def set_texel_density(image: np.ndarray) -> np.ndarray:
    """
    Set texel density using AI.
    """
    set_texel_image = image
    return set_texel_image


def add_grunge(image: np.ndarray, grunge_map_path:str) -> np.ndarray:
    """
    Add grunge map to texture.
    
    Parameters:
        image_path (str): Path to the base texture image.
        grunge_map_path (str): Path to the grunge map image.
    
    Returns:
        process_image (numpy.ndarray): The image with the grunge map applied.
    """
    
    # Read the grunge map
    grunge_map = cv2.imread(grunge_map_path, cv2.IMREAD_GRAYSCALE)
    if grunge_map is None:
        raise ValueError(f"Grunge map at {grunge_map_path} could not be read.")
    
    # Resize grunge map to match the base image size
    grunge_map_resized = cv2.resize(grunge_map, (image.shape[1], image.shape[0]))
    
    # Convert grunge map to 3 channels
    grunge_map_colored = cv2.cvtColor(grunge_map_resized, cv2.COLOR_GRAY2BGR)
    
    # Overlay the grunge map on the base image
    process_image = cv2.addWeighted(image, 0.8, grunge_map_colored, 0.2, 0)
    
    return process_image


def remove_artifacts(input_image: np.ndarray) -> np.ndarray:
    """
    Remove small artefacts by using AI and smoothing.
    """
    print("Placeholder feature")
    pass
    process_image = input_image
    return process_image


def make_tiling(img: np.ndarray) -> np.ndarray:
    """
    Make texture tiling for game engines using image processing.
    
    Parameters:
        img (numpy.ndarray): The input image to be tiled.
    
    Returns:
        process_image (numpy.ndarray): The tiling texture image.
    """
    # Ensure image is in float32 for blending
    img = img.astype(np.float32) / 255.0
    
    # Split the image into four quadrants and swap them
    h, w, c = img.shape
    half_h, half_w = h // 2, w // 2
    
    top_left = img[:half_h, :half_w]
    top_right = img[:half_h, half_w:]
    bottom_left = img[half_h:, :half_w]
    bottom_right = img[half_h:, half_w:]
    
    # Swap quadrants
    blended = np.zeros_like(img)
    blended[:half_h, :half_w] = bottom_right
    blended[:half_h, half_w:] = bottom_left
    blended[half_h:, :half_w] = top_right
    blended[half_h:, half_w:] = top_left
    
    # Apply Gaussian blur to smooth the seams
    blended = cv2.GaussianBlur(blended, (31, 31), 0)
    
    # Normalize back to 0-255
    blended = np.clip(blended * 255.0, 0, 255).astype(np.uint8)
    
    return blended


def force_square(img: np.ndarray) -> np.ndarray:
    """
    Force resolution to square by cropping the image to the smallest dimension.
    
    Parameters:
        image_path (str): Path to the input image.
    
    Returns:
        process_image (numpy.ndarray): The cropped square image.
    """
    
    # Get image dimensions
    height, width, _ = img.shape
    
    # Determine the size of the square
    square_size = min(height, width)
    
    # Calculate the cropping coordinates
    top = (height - square_size) // 2
    bottom = top + square_size
    left = (width - square_size) // 2
    right = left + square_size
    
    # Crop the image to the square
    process_image = img[top:bottom, left:right]
    
    return process_image


def generate_metallic(input_image: np.ndarray, is_metallic:int = 0) -> np.ndarray:
    """
    Generate a basic metallic map for the image.
    
    Parameters:
        image_path (str): Path to the input image.
        material_preset (dict): Dictionary containing material properties.
    
    Returns:
        process_image (numpy.ndarray): The generated metallic map.
    """
    
    # Create a metallic map based on the is_metallic value
    if is_metallic:
        metallic_texture = np.full_like(input_image, 255)  # Full white for metallic
    else:
        metallic_texture = np.full_like(input_image, 0)  # Full black for non-metallic
    
    return metallic_texture


def convert_image(input_image: np.ndarray, target_format: str = "Don't Convert") -> np.ndarray:
    """
    Convert an image to a different format and return the image in the target format.
    
    Parameters:
        input_image (numpy.ndarray): The input image to be converted.
        target_format (str): The target format to convert the image to. Choices are 'PNG', 'JPG', 'BMP', or no conversion.
    
    Returns:
        converted_image (numpy.ndarray): The converted image in the target format.
    """
    
    # Ensure the target format is uppercase for Pillow library
    PILformat = target_format.upper()
    
    # Convert the input NumPy array to a Pillow Image so we can do conversion
    img = Image.fromarray(input_image)
    
    # Create an in-memory bytes buffer
    img_byte_arr = io.BytesIO()
    
    # Save the image to the bytes buffer in the desired format
    img.save(img_byte_arr, format=PILformat)
    
    # Retrieve the byte data of the image
    img_byte_arr.seek(0)  # Ensure we are at the beginning of the byte buffer
    
    # Open the image from the byte array (Pillow automatically detects the format)
    img = Image.open(img_byte_arr)
    
    # Convert the Pillow Image back to a NumPy array
    image_array_result = np.array(img)

    # Return the resulting NumPy array
    return image_array_result
