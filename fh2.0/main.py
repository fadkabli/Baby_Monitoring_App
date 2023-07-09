from threading import Thread
from flask import Flask, render_template, Response, request
import cv2
import numpy as np
import time
import json
from traking import PoseEstimation, CameraOps
from pushbullet import Pushbullet
import requests
import time
from pygame import mixer


# Set the camera source to be used for capturing video
# "0" refers to the webcam, or provide the path to a video file
################### INPUTS HERE ################################
camera_source ='baby_aboveNight2.avi'  # put "0" for webcam

################### INPUTS HERE ################################


# Create a CameraOps object with the specified camera source
camera = CameraOps(camSource=camera_source)

# Create a Flask app object
app = Flask(__name__)
# Global variable to keep track of whether a notification has been sent
message_sent = False


##########   GLOBAL variables ##########
# Global dictionary to store the detection results
detected_data = {"warning_message" : "", "warning_severity" : "LOW"}

#PUSH_BULLET_API_KEY = "xxxxxx" # PUSHBULLET API KEY WILL BE HERE

# Set the delay time between notifications in milliseconds
NOTIFICATION_DELAY = 30000 # in miliseconds (1 minutes delay = 60seconds * 1000 miliseconds)

# Keep track of the time of the last warning
warning_time = 0 # Recent warning time in miliseconds

#pb = Pushbullet(PUSH_BULLET_API_KEY)

################################################### DETECTION [START]########################################################
# Function called from javascript to get the detection results
@app.route("/getResult")
def getResult():
    """Function called from javascript after every 0.5 seconds 
    in id_assigning.html for displaying person recognized and QR code"""

    global warning_time

    global NOTIFICATION_DELAY

    current_time = int(round(time.time() * 1000))
    # Initialize mixer for playing sound

    mixer.init() #calling mixer for sound
    if detected_data['warning_severity'] == 'HIGH':

        #adding sound file to mixer
        mixer.music.load('sound.wav')
        mixer.music.play() #playing sound
        time.sleep(0.5)
        # Baby in danger, send notification if it's first warning or warning after 1 minute delay
        # Send notification if it's the first warning or warning after 1 minute delay
        warning_time_with_delay = warning_time + NOTIFICATION_DELAY

        if warning_time == 0 or current_time > warning_time_with_delay:
            warning_time = current_time  # Update warning time
            send_notification(detected_data['warning_message'])

  # Stop playing sound if severity is LOW or MEDIUM
    elif detected_data['warning_severity'] == 'LOW' or detected_data['warning_severity'] == 'MEDIUM':

        mixer.music.stop()  #stopping the sound

  # Convert detected_data dictionary to JSON string and return
    object_json = json.dumps(detected_data)
   
    return object_json

def get_detection_result():
    """This function yeilds frames for streaming on detection/ recognition page. Also it stores realtime
    face detected person name and QR code values in dictionary called detected_data"""
    global detected_data  # use the global variable detected_data
    # Get the current time in seconds
    timest = time.time()
    
    # Start a thread to capture camera frames
    t1 = Thread(target = camera.start_cam_stream)   
    t1.start()
    # Continue capturing frames as long as the camera is set to stream
    if camera.toStream==True:
        while True:
             # If there is a current frame available, encode it as a JPEG image and store warning data
            if camera.curFrame is not None:
                ret, buffer = cv2.imencode('.jpg', camera.curFrame)
                detected_data["warning_message"] = camera.warning_message
                detected_data["warning_severity"] = camera.warning_severity
                # Convert the frame buffer to bytes and yield it to the streaming page
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            else:
                time.sleep(0.5) # Wait for a short period if there is no current frame
            if camera.toStream==False:
                break  # Stop streaming if the camera is set to not stream





@app.route("/vid_stream")
def vid_stream():
    """ Function called from id_assigning.html to render steam to show on web page """   
    return Response(get_detection_result(), mimetype='multipart/x-mixed-replace; boundary=frame')


################################################### DETECTION [END] ########################################################
@app.route("/stop_all_cameras", methods=['POST'])
def stop_all_cameras():
    """Function to stop all cameras."""
    global camera
    if camera is not None:
        camera.toStream = False

    return render_template('index.html')

@app.route('/start_stream', methods=['post'])
def start_stream():
    """Function to start the camera stream."""
    global camera
    if camera is not None:
        camera.toStream = True

    return render_template('index.html')


@app.route('/', methods=['GET','POST'])
def index():
    """Function to start the camera stream on index.html."""
    global camera
    stop_all_cameras()
    camera.toStream = True

    return render_template('index.html')

#send notification to user device
def send_notification(warning_message):
    title = "BABY MONITORING"
    body = warning_message
   # pb.push_note(title, body) - Notification API commented out for testing purposes
    return 'Notification Sent'


if __name__ == "__main__":

   app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
    #app.run(debug=True, host="172.20.10.8", port=5000, use_reloader=False)
