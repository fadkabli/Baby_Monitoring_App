from threading import Thread
from flask import Flask, Response, request, jsonify, render_template
import cv2
import numpy as np
import time
from LivePoseEstimation_class import PoseEstimation, CameraOps

# INPUTS HERE
camera_source = "baby_aboveNight2.avi"  # for video file
# camera_source = "0"  # put "0" for webcam

camera = CameraOps(camSource=camera_source)
app = Flask(__name__)

# GLOBAL variables
detected_data = {"warning_message": "", "warning_severity": "LOW"}


@app.route("/getResult")
def get_result():
    """Function called from javascript after every 0.5 seconds
    in index.html for displaying person recognized and QR code"""

    return jsonify(detected_data)


def get_detection_result():
    """This function yields frames for streaming on detection/ recognition page.
    Also it stores realtime face detected person name and QR code values
    in a dictionary called detected_data"""
    global detected_data
    timest = time.time()

    t1 = Thread(target=camera.start_cam_stream)
    t1.start()
    if camera.toStream == True:
        while True:
            if camera.curFrame is not None:
                ret, buffer = cv2.imencode('.jpg', camera.curFrame)
                detected_data["warning_message"] = camera.warning_message
                detected_data["warning_severity"] = camera.warning_severity

                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            else:
                time.sleep(0.5)
            if camera.toStream == False:
                break


@app.route("/vid_stream")
def vid_stream():
    """Function called from index.html to render stream to show on web page"""
    return Response(get_detection_result(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/stop_all_cameras", methods=['POST'])
def stop_all_cameras():
    global camera
    if camera is not None:
        camera.toStream = False

    return jsonify({"status": "success"})


@app.route('/start_stream', methods=['POST'])
def start_stream():
    global camera
    if camera is not None:
        camera.toStream = True

    return jsonify({"status": "success"})


@app.route('/')
def index():
    global camera
    stop_all_cameras()
    camera.toStream = True

    return render_template('index1.html')


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.before_first_request
def activate_job():
    def run_job():
        while True:
            print("Running scheduled job...")
            time.sleep(60)

    thread = Thread(target=run_job)
    thread.start()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
