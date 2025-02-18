import cv2
import numpy as np
from PIL import Image

def process_image(input_filepath, intensity_factor=2.0):
    """
    Process an image by normalizing it to grayscale and adjusting its intensity.
    
    Parameters:
        input_filepath (str): Path to the uploaded image file.
        intensity_factor (float): Factor by which the intensity will be adjusted.

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
    
    return img_normalized

def resize_and_crop(image_path, size=(512, 512)):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        width, height = img.size
        
        left = (width - size[0]) / 2
        top = (height - size[1]) / 2
        right = (width + size[0]) / 2
        bottom = (height + size[1]) / 2

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
