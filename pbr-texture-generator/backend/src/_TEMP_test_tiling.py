from image_processing import make_tiling
import cv2

test_image_valid = "tests/image.jpg"

output_image = "tests/tiling_image.jpg"

# Load the image into np.ndarray
image = cv2.imread(test_image_valid)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Ensure the image dimensions are suitable for tiling
height, width, _ = image.shape
if height % 2 != 0 or width % 2 != 0:
    raise ValueError("Image dimensions must be even for tiling.")

# Process the image
processed_image = make_tiling(image)

cv2.imwrite(output_image, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))

