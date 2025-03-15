import pytest
from io import BytesIO
import json
from flask import Flask, jsonify

# Dummy Flask app
app = Flask(__name__)

# Dummy route for testing
@app.route('/upload', methods=['POST'])
def upload_image():
    # This is just a dummy route that will always return a 200 status
    return jsonify({"message": "Images processed", "files": ["test_image.jpg"]}), 200

# Create a test client fixture
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Dummy test to ensure everything works
def test_upload_image(client):
    # Prepare a dummy image
    image_data = BytesIO(b"Fake image content for testing")
    image_data.filename = "test_image.jpg"  # Set the filename attribute

    # Prepare mock preferences (as you use it in the upload route)      
    preferences = {
        "target_export_resolution": "512x512",
        "use_ai_segmentation": False,
        "manual_material_selection": None,
        "apply_ai_upscale": False,
        "pbr_standardize": False,
        "set_texel_ai": False,
        "normal_bump": False,
        "add_grunge": False,
        "remove_artifacts": False,
        "make_tiling": False,
        "force_square": False
    }

    # Convert preferences to JSON string
    preferences_json = json.dumps(preferences)

    # Send the POST request to the `/upload` endpoint
    response = client.post(
        '/upload',
        data={
            'file': (image_data, 'test_image.jpg'),
            'preferences': preferences_json
        },
        content_type='multipart/form-data'
    )

    # Assert the response status code and message
    assert response.status_code == 200
    assert 'Images processed' in response.json['message']
