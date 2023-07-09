from flask import Flask, jsonify, request
import cv2
import numpy as np
from mtcnn import MTCNN

app = Flask(__name__)

detector = MTCNN()

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
        results = detector.detect_faces(img)

        # check if any face is covered
        covered_faces = []
        for result in results:
            x, y, w, h = result['box']
            keypoints = result['keypoints']
            left_eye = keypoints['left_eye']
            right_eye = keypoints['right_eye']
            nose = keypoints['nose']
            mouth_left = keypoints['mouth_left']
            mouth_right = keypoints['mouth_right']
            
            # calculate the ratio of the distance between facial keypoints to the width of the face
            eye_distance = np.linalg.norm(np.array(left_eye) - np.array(right_eye))
            nose_distance = np.linalg.norm(np.array(nose) - np.array([(mouth_left[0] + mouth_right[0]) / 2, (mouth_left[1] + mouth_right[1]) / 2]))
            
            if 'chin' in keypoints:
                chin = keypoints['chin']
                chin_distance = np.linalg.norm(np.array(nose) - np.array(chin))
                face_height = h
                chin_ratio = chin_distance / face_height
                if chin_ratio < 0.4:
                    covered_faces.append({'x': x, 'y': y, 'width': w, 'height': h})
            else:
                # if the 'chin' key is not present, we assume that the face is not covered
                covered_faces.append({'x': x, 'y': y, 'width': w, 'height': h})
        
        # return the results as a JSON object
        num_faces = len(results)
        num_covered_faces = len(covered_faces)
        results = {
            'num_faces': num_faces,
            'num_covered_faces': num_covered_faces,
            'faces': covered_faces
        }
        if num_covered_faces > 1:
            return jsonify({'warning': 'Some faces are covered!'}), 400
        else:
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
