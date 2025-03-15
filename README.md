# MapMorph: AI-Powered PBR Texture Generation

# Project Introduction



In the world of computer graphics and game development, manually creating PBR (Physically Based Rendering) specular textures is a time-consuming and intricate process. This workflow often requires expensive software licenses and high-end hardware setups, making it difficult for smaller teams and independent artists, such as students or those with limited financial ability to access high-quality texture generation tools.

![PBR Rendering Sample Image](https://learnopengl.com/img/pbr/ibl_specular_result_textured.png)

MapMorph is an innovative web-based solution that automates the generation of PBR textures directly from real-world photos. This tool streamlines the texture creation process, removing common barriers such as:

- The need for licensed software like Substance Painter
- Expensive hardware requirements
- Installation processes
- Platform dependence

By leveraging AI-powered enhancements and modern web technologies, MapMorph provides a fast, scalable, and accessible method for creating high-quality textures. It’s designed to make texture creation easier for 3D artists, game developers, and other professionals in the creative industries.

## Key Features

- Automated Texture Generation: Quickly convert real-world images into roughness, albedo, and normal maps with a single click.

- PBR value standardizer: This unique feature of MapMorph will make sure all of your textures adhere to the Physically Based database preset of PBR values, ensuring all of your textures work in cohesion. You can even use custom presets for Unreal or Unity or even upload your own!

- Support for multiple industry standard workflows: Roughness/Metallic and Specular/Glossiness workflows as well as Bump mapping are supported.

- User-Friendly Interface: Intuitive and accessible for both beginners and seasoned professionals.

- Scalable and Performant: Built using modern web technologies for fast, efficient processing, even with larger image files.

- AI-Powered Enhancements: Optional AI-based material segmentation that intelligently analyzes images to provide advanced texture results.

- Cross-Platform: No installation or hardware requirements. Works seamlessly across platforms using only a browser.

# Demo

You can explore a live demo of MapMorph on  [[http://mcp140.pythonanywhere.com](http://mcp140.pythonanywhere.com)] and see the texture generation process in action. The demo is hosted online, so no installation is required—simply upload your image, process it, and download the result.

Check out a demo on YouTube!

[![MapMorph Demo Video](https://img.youtube.com/vi/P6Kfp0JXXEU/0.jpg)](https://www.youtube.com/watch?v=P6Kfp0JXXEU)

**Thanks for the thumbs up 😀👍**

# Step-by-Step Usage

### 1. Upload Your Image:
Drag and drop or select an image from your computer to begin. Supported formats: JPG, PNG, and TIFF.

### 2.Process the Image: 
Once the image is uploaded, click the "Process" button to automatically generate PBR textures. The AI-powered backend will analyze the image and produce roughness, albedo, and normal maps.

### 3.Download the Textures: 
After processing, you can download the generated textures in either PNG or TGA format. Perfect for use in game engines like Unity, Unreal Engine, or 3D modeling software.
     
Example Output: After processing, MapMorph generates the following PBR texture maps:

- Albedo Map (Diffuse)
- Roughness Map
- Normal Map

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

Again note that a live version on the website is available at [[http://mcp140.pythonanywhere.com](http://mcp140.pythonanywhere.com)]

## Prerequisites

To run this project locally, you need the following installed on your machine:

- Python 3.8+

- pip (Python package manager)

Dependancies can be installed by running pip install requirements.txt

# Installation and Running Instructions

If you wish to deploy the web app locally on your machine, here is a step by step series of examples that tell you how to get a development env running in no time!

## 1. Clone the repository
```bash
git clone https://github.com/MetePolat825/MapMorph_Web_App_PBR_Texture_Generation.git
```

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Navigate to the backend folder
```bash
cd pbr-texture-generator/backend
```

## 4. Run the Flask app on the local server 127.0.0.1:5000
```bash
python app.py
```

## 5. Access the application
Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000) to access the local build of the application.

At this point you may try out all the basic features with no restrictions! Awesome stuff.

# Built With

*  Frontend: Vue.js, Bootstrap, Three.js

* Backend: Flask, OpenCV, NumPy

* Database: SQLite

* Hosting: Heroku

# Project Folder Structure

```bash
├── backend
   ├── presets <- PBR value preset CSVs
   ├── processed <- final processed images to be downloaded to the user
   ├── src <- image processing scripts and other secondary logic
   ├── static <- images, icons, CSS
   ├── templates <- frontend HTML templates
   ├── tests <- unit tests for app and image processing logic
   ├── uploads <- user upload directory
   ├── app.py <- Entry Point for the program
├── frontend <- contains Javascript frontend components (work in progress)
├── docs <- contains local copy of documentation for offline access
├── README.md <- Developer Documentation
├── requirements.txt <- required libraries for local installation
```
## CI/CD Workflow

This project uses **GitHub Actions** for continuous integration and continuous deployment (CI/CD). The GitHub Actions workflow automates the following tasks:

- **Code Testing**: Each push or pull request triggers automated tests using `pytest` to ensure the quality of the code.
- **Deployment**: After passing the tests, the application is automatically deployed to **PythonAnywhere**, a platform that hosts Python applications.

### GitHub Actions

The CI/CD pipeline is defined in the `.github/workflows/ci.yml` file. The pipeline includes the following steps:
1. **Install dependencies**: Install required dependencies from `requirements.txt`.
2. **Run tests**: Execute tests using `pytest` to ensure the code works correctly.
3. **Deploy to PythonAnywhere**: Upon successful tests, the app is deployed to PythonAnywhere.

### PythonAnywhere Deployment

The project is hosted on **PythonAnywhere**, which provides a cloud-based platform for Python applications. After the GitHub Actions workflow completes, the application is automatically deployed to PythonAnywhere using the provided deployment scripts. The app can be accessed from [PythonAnywhere](https://mcp140.pythonanywhere.com/).

For more details on setting up the GitHub Actions workflow and deploying to PythonAnywhere, check out the following documentation:

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PythonAnywhere Documentation](https://help.pythonanywhere.com/)

# Roadmap

## Future Features:
- Support for additional texture maps (e.g., specular, metallic)
- Enhanced AI segmentation for complex materials like fabric, wood, and metal
- User authentication for saving custom textures and preferences
- Integration with game engines for direct texture importing
- API access for students and corporate plans custom to your business needs

# Contributing

We welcome contributions! Please read our Contributing Guidelines and Code of Conduct before getting started.

1. Fork the repository.

2. Create a new branch for your feature or bugfix.

3. Make your changes and test them thoroughly.

4. Submit a pull request with a detailed description of your changes.

# Authors

* **MetePolat825** - *Initial work* - [MetePolat825](https://github.com/MetePolat825)

See also the list of [contributors](https://github.com/MetePolat825/MapMorph_Web_App_PBR_Texture_Generation/contributors) who participated in this project.

# License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

# Acknowledgments

* OpenCV for image processing.

* Flask for the backend framework.

* Three.js for 3D visualization.

* Best README Template for inspiration.

