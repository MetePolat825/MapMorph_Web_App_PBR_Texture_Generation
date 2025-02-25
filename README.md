# MapMorph: AI-Powered PBR Texture Generation

MapMorph is a web-based application designed to automate and streamline the generation of Physically Based Rendering (PBR) textures from real-world photos. It provides an intuitive, scalable, and accessible solution for 3D artists and game developers, enabling them to create high-quality textures with minimal effort.

Features

- Automated Texture Generation: Convert images into roughness maps with a single click.
- User-Friendly Interface: Intuitive and accessible for both beginners and professionals.
- Scalable and Performant: Built with modern web technologies for fast and efficient processing.
- AI-Powered Enhancements: Optional AI-based material segmentation for advanced workflows.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You can try out MapMorph without any installations using the live website: [[http://mcp140.pythonanywhere.com](http://mcp140.pythonanywhere.com)]

To run this project locally, you need the following installed on your machine:

- Python 3.8+

- pip (Python package manager)

Dependancies can be installed by running pip install requirements.txt

- Flask (for the backend)

- OpenCV (for image processing)

- SQLite (for user authentication and preferences)


# Installation and Running Instructions

If you wish to deploy the web app locally on your machine, here is a step by step series of examples that tell you how to get a development env running in no time!

## 1. Clone the repository
```bash
git clone https://github.com/your-username/pbr-texture-generator.git
```

## 2. Navigate to the backend folder
```bash
cd pbr-texture-generator/backend
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Run the Flask app
```bash
python app.py
```

## 5. Access the application
Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000) to access the local build of the application.


## Example Usage

1. Upload Images: Drag and drop or select images to upload.

2. Process Images: Click "Process" to generate PBR textures.

3. Download Results: Download the processed textures in PNG or TGA format.

End with an example of getting some data out of the system or using it for a little demo


## Running the tests

To run automated tests for this system, follow these steps:

1. Navigate to the tests/ directory:
```
cd tests/
```
2. Run the test suite:
```
python -m unittest discover
```

### Break down into end to end tests

These tests simulate user interactions with the application, such as uploading images, processing them, and downloading the results.

```
def test_image_upload(self):
    response = self.client.post('/upload', data={'file': (io.BytesIO(b"test image data"), 'filename': 'test.jpg'})
    self.assertEqual(response.status_code, 200)
```

### And coding style tests

These tests ensure the code follows PEP 8 standards and other best practices.

```
flake8 .
```

## Deployment

To deploy this project on a live system, follow these steps:

1. Set up a production server (e.g., Heroku, AWS, or PythonAnywhere).

2. Install dependencies:
```
pip install -r requirements.txt .
```
3. Run the Flask app:
```
python app.py
```
4. Configure environment variables (e.g., database credentials, API keys).

## Built With

*  Frontend: Vue.js, Bootstrap, Three.js

* Backend: Flask, OpenCV, NumPy

* Database: SQLite

* Hosting: Heroku 

## Contributing

We welcome contributions! Please read our Contributing Guidelines and Code of Conduct before getting started.

1. Fork the repository.

2. Create a new branch for your feature or bugfix.

3. Make your changes and test them thoroughly.

4. Submit a pull request with a detailed description of your changes.

## Versioning

N/A

## Authors

* **MetePolat825** - *Initial work* - [MetePolat825](https://github.com/MetePolat825)

See also the list of [contributors](https://github.com/MetePolat825/MapMorph_Web_App_PBR_Texture_Generation/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* OpenCV for image processing.

* Flask for the backend framework.

* Three.js for 3D visualization.

* Best README Template for inspiration.

