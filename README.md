SkinBurnPro
SkinBurnPro is an AI-powered application designed to classify burn severity based on images. It leverages deep learning techniques and ensemble methods to achieve high accuracy in predicting different degrees of burns. The application is built with FastAPI and Streamlit, and the project has been managed using Azure DevOps with CI/CD pipelines. The application is containerized and pushed to Docker Hub for easy deployment.

Features
Burn Classification: Classifies images into first, second, and third-degree burns using a pre-trained deep learning model.
User Authentication: Secure user registration and login with token-based authentication.
Image Upload: Allows users to upload images for burn classification.
Feedback System: Users can submit feedback on the classification results.
Logging and Reporting: Comprehensive logging and downloadable reports for users after classification.
Streamlit Interface: A user-friendly interface for interacting with the application.
CI/CD Pipelines: Automated testing and deployment using Azure DevOps.
Containerization: The application is containerized using Docker and available on Docker Hub.

Project Structure
├── project_dir
│   ├── models
│   ├── pipelines
│   ├── services
│   ├── streamlit_app.py
│   ├── main.py
│   ├── requirements.txt
├── Dockerfile
├── Dockerfile.streamlit
├── docker-compose.yml
├── init.sql
└── README.md

Technologies Used
TensorFlow: For model training and inference.
FastAPI: Backend API for handling requests and user management.
Streamlit: For building an interactive user interface.
PostgreSQL: Database for storing user data and classifications.
Docker: Containerization of the application for easy deployment.
Azure DevOps: For project management, CI/CD pipelines, and automated deployment.

Setup Instructions
Clone the Repository:

Copy code
git clone https://github.com/Chukwuemekaokafor77/SkinBurnPro.git
cd SkinBurnPro
Install Dependencies:
You can either set up the project locally or use Docker.

Local Setup:

pip install -r requirements.txt

Docker Setup:
Ensure you have Docker installed and running. Then, build and start the services using:
docker-compose up --build
Environment Variables:
Create a .env file with the following variables:
DB_USERNAME=postgres
DB_PASSWORD=0000
DB_HOSTNAME=db
DB_PORT=5432
DB_NAME=group6
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
EMERGENCY_EMAIL=your_emergency_email@gmail.com
Initialize the Database:
Ensure that the database is initialized by running the init.sql script.

Usage
FastAPI: The FastAPI service will be running on http://localhost:8000.
Streamlit: Access the Streamlit interface at http://localhost:7815.

Example Requests
Register User:
POST /register
Body: {
    "username": "your_username",
    "password": "your_password"
}
Login:

bash
Copy code
POST /login
Body: {
    "username": "your_username",
    "password": "your_password"
}
Upload Image for Classification:

POST /predict
Header: Authorization: Bearer your_token
Body: {
    "file": <your_image_file>
}
Docker
The application is fully containerized. You can pull the latest image from Docker Hub:

docker pull emekamikolo777/SkinBurnPro
To run the container, use:
docker-compose up --build

Contributing
Contributions are welcome! Please follow the standard GitHub workflow for contributing to this project.

Fork the repository.
Create your feature branch (git checkout -b feature/new-feature).
Commit your changes (git commit -m 'Add new feature').
Push to the branch (git push origin feature/new-feature).
Open a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

