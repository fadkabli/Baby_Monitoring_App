# Baby_Monitoring_App

# Baby Monitoring App

This is a Python Flask application that allows you to detect faces in an image and determine if any faces are covered. It uses the MTCNN (Multi-task Cascaded Convolutional Networks) face detection algorithm.

# Prerequisites

Python 3.x
Flask
OpenCV
NumPy
MTCNN
Installation

Clone the repository to your local machine.

Install the required dependencies using the following command:

pip install flask opencv-python numpy mtcnn

# Usage

# Run the Flask application by executing the following command:

python app.py

Access the application by opening a web browser and navigating to http://localhost:5000.
Upload an image file using the provided form.
Click the "Detect" button to detect faces in the uploaded image.
The application will return the number of detected faces and the number of faces that are covered. If any faces are covered, a warning message will be displayed.
API Endpoint

The application provides a single API endpoint /detect_faces that accepts a POST request with an image file. It returns a JSON response containing information about the detected faces and whether any faces are covered.

# Example POST request:

POST /detect_faces

Request Body:
- image: [image file]

# Example Response:

{
  "num_faces": 2,
  "num_covered_faces": 1,
  "faces": [
    {
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 200
    }
  ]
}

# Notes

The application uses the MTCNN face detection algorithm to detect faces in the uploaded image.

It checks if any faces are covered by calculating the ratio of distances between facial keypoints and the width of the face.

If the 'chin' key is present in the detected keypoints, it calculates the chin ratio and considers the face covered if the ratio is below 0.4. Otherwise, it assumes the face is not covered.

The application supports the detection of multiple faces and returns information about each detected face.

The HTML form on the application's main page allows you to upload an image file and perform face detection.

The application can be extended or customized to fit specific use cases and requirements.

Feel free to explore and enhance this baby monitoring app according to your needs. Happy coding!
