from flask import Flask, jsonify, request
import cv2
import numpy as np

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

@app.route('/detect_faces', methods=['GET', 'POST'])
def detect_faces():
    if request.method == 'POST':
        # read the image file from the request
        file = request.files['image']
        img_bytes = file.read()

        # decode the image bytes into a numpy array
        img_np = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        # detect faces in the image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        # convert int32 to int
        faces = [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

        # return the results as a JSON object
        results = {
            'num_faces': len(faces),
            'faces': [{'x': x, 'y': y, 'width': w, 'height': h} for (x, y, w, h) in faces]
        }
        return jsonify(results)
    else:
        return '''
            <html>
                <body>
                    <h1>Detect Faces</h1>
                    <form method="post" enctype="multipart/form-data">
                        <input type="file" name="image">
                        <input type="submit" value="Detect">
                    </form>
                </body>
            </html>
        '''
    if __name__ == '__main__':
    # run the app on IP address 119.158.62.187 and port 5000
    app.run(host='119.158.62.187', port=5000)

