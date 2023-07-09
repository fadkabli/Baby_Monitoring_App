from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

# Load the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load the face mask detector model
mask_net = cv2.dnn.readNet('res10_300x300_ssd_iter_140000_fp16.caffemodel', 'deploy.prototxt')

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

def detect_faces(frame):
    """Detect faces in a video frame using the Haar Cascade classifier."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faces:
        # Extract the face region from the frame
        face = frame[y:y+h, x:x+w]
        # Preprocess the face image for facemask detection
        blob = cv2.dnn.blobFromImage(face, 1.0, (300, 300), (104.0, 177.0, 123.0))
        # Pass the face image through the facemask detection model
        mask_net.setInput(blob)
        detections = mask_net.forward()
        # Get the confidence score for facemask detection
        confidence = detections[0, 0, 0, 2]
        # Draw the facemask detection result on the frame
        if confidence > 0.9:
            label = "Mask Detected"
            color = (0, 255, 155)
        else:
            label = "Mask Not Detected"
            color = (0, 54, 255)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        print("Number of faces detected: ", len(faces))
    
    # Increase brightness of the frame
    brightness = -10
    frame = cv2.addWeighted(frame, 1 + brightness / 100.0, np.zeros(frame.shape, dtype=frame.dtype), 0, brightness)
    return frame, len(faces) # return the number of faces detected

def generate():
    """Generate a video stream of face detection frames."""
    video_capture = cv2.VideoCapture(0)
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            frame, num_faces = detect_faces(frame)
            print("Number of faces detected:", num_faces)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n' +
                   b'<h4> Number of faces detected: ' + str(num_faces).encode() + b'</h4>')
                   
    video_capture.release()

@app.route('/video_feed')
def video_feed():
    """Stream a video feed of face detection frames."""
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
