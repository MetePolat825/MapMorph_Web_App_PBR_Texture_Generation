import cv2

from image_processing import generate_normal_map

test_image_valid = "tests/image.jpg"

output_image = "tests/normal_image.jpg"

# Load the image into np.ndarray
image = cv2.imread(test_image_valid)

# Process the image
processed_image = generate_normal_map(image, normal_configuration="Normal Map")

cv2.imwrite(output_image, processed_image)
