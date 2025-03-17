import unittest
import numpy as np
from unittest.mock import patch, MagicMock

from image_processing import pre_process_check, convert_image

test_image_valid = "tests/image.jpg"
# test_image_invalid = "tests/test_image_valid.jpg"


class TestPreProcessCheck(unittest.TestCase):

    @patch('os.path.getsize')
    def test_invalid_extension(self, mock_getsize):
        # Simulating a file with a non-supported extension
        filepath = 'image.bmp'
        mock_getsize.return_value = 1000  # Mocked file size
        
        with self.assertRaises(ValueError) as context:
            pre_process_check(filepath)
        
        self.assertEqual(str(context.exception), "Invalid file extension. Only .png, .jpg, .jpeg, and .tga are allowed.")
    
    @patch('os.path.getsize')
    def test_file_size_zero(self, mock_getsize):
        # Simulating a file with size 0 (empty file)
        filepath = 'image.png'
        mock_getsize.return_value = 0  # Mocked file size
        
        with self.assertRaises(ValueError) as context:
            pre_process_check(filepath)
        
        self.assertEqual(str(context.exception), "File size is 0. The file may be corrupted.")

    @patch('os.path.getsize')
    def test_file_size_too_large(self, mock_getsize):
        # Simulating a file that's too large (> 10 MB)
        filepath = 'image.png'
        mock_getsize.return_value = 11 * 1024 * 1024  # 11 MB
        
        with self.assertRaises(ValueError) as context:
            pre_process_check(filepath)
        
        self.assertEqual(str(context.exception), "File size is too large. Maximum allowed size is 10 MB.")

    @patch('cv2.imread')
    def test_image_dimensions_too_small(self, mock_imread,test_image_valid):
        # Simulating an image with dimensions smaller than 256x256
        filepath = test_image_valid
        mock_imread.return_value = MagicMock(shape=(100, 100, 3))  # Mocked image with small dimensions
        
        with self.assertRaises(ValueError) as context:
            pre_process_check(filepath)
        
        self.assertEqual(str(context.exception), "Image dimensions are too small. Minimum size is 256x256 pixels.")

    @patch('cv2.imread')
    def test_image_dimensions_valid(self, mock_imread,test_image_valid):
        # Simulating a valid image with dimensions >= 256x256
        filepath = test_image_valid
        mock_imread.return_value = MagicMock(shape=(300, 300, 3))  # Mocked valid image dimensions
        
        # No exception should be raised
        try:
            pre_process_check(filepath)
        except ValueError:
            self.fail("pre_process_check raised ValueError unexpectedly!")

    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_image_readability_corrupted(self, mock_getsize, mock_image_open):
        # Simulating a corrupted image
        filepath = 'corrupted_image.jpg'
        mock_getsize.return_value = 5000  # Mocked file size
        mock_image_open.side_effect = (IOError("Image is corrupted"))
        
        with self.assertRaises(ValueError) as context:
            pre_process_check(filepath)
        
        self.assertTrue("Image is corrupted" in str(context.exception))

    @patch('PIL.Image.open')
    @patch('os.path.getsize')
    def test_image_readability_valid(self, mock_getsize, mock_image_open):
        # Simulating a valid image
        filepath = 'valid_image.jpg'
        mock_getsize.return_value = 5000  # Mocked file size
        mock_image_open.return_value = MagicMock()
        
        # No exception should be raised
        try:
            pre_process_check(filepath)
        except ValueError:
            self.fail("pre_process_check raised ValueError unexpectedly!")
                    

class TestImageConversion(unittest.TestCase):
    def setUp(self):
        # Create a simple test image (100x100 RGB)
        self.image_array = np.random.rand(100, 100, 3) * 255  # 100x100 RGB image
        self.image_array = self.image_array.astype(np.uint8)
    
    def test_convert_to_png(self):
        # Test converting to PNG format
        converted_image, format = convert_image(self.image_array, "PNG")
        self.assertEqual(format, ".png")
        self.assertEqual(converted_image.shape, self.image_array.shape)
        self.assertTrue(np.issubdtype(converted_image.dtype, np.uint8))

    def test_convert_to_jpg(self):
        # Test converting to JPG format
        converted_image, format = convert_image(self.image_array, "JPG")
        self.assertEqual(format, ".jpg")
        self.assertEqual(converted_image.shape, self.image_array.shape)
        self.assertTrue(np.issubdtype(converted_image.dtype, np.uint8))

    def test_convert_to_bmp(self):
        # Test converting to BMP format
        converted_image, format = convert_image(self.image_array, "BMP")
        self.assertEqual(format, ".bmp")
        self.assertEqual(converted_image.shape, self.image_array.shape)
        self.assertTrue(np.issubdtype(converted_image.dtype, np.uint8))

    def test_no_conversion(self):
        # Test no conversion (i.e., target_format = "Don't Convert")
        converted_image, format = convert_image(self.image_array, "Don't Convert")
        self.assertEqual(format, ".don't convert")
        self.assertTrue(np.array_equal(converted_image, self.image_array))

    def test_invalid_format(self):
        # Test an invalid format (this might raise an error, so we handle that)
        with self.assertRaises(ValueError):
            convert_image(self.image_array, "INVALID_FORMAT")
    
    def test_convert_empty_image(self):
        # Test the function with an empty image array (0x0 image)
        empty_image = np.zeros((0, 0, 3), dtype=np.uint8)
        converted_image, format = convert_image(empty_image, "PNG")
        self.assertEqual(format, ".png")
        self.assertEqual(converted_image.shape, (0, 0, 3))


if __name__ == '__main__':
    unittest.main()
