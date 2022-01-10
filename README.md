# FaceEyeDetection
This is example of face and eye detection from camera video source. Here we have used cascade classifier for detection of faces and eyes. Also we are taking snap shot of our region of interest of face detected with eyes and save it also. Here I have used two xml files which helps us to detect face and eye from frame. From link https://github.com/opencv/opencv/tree/master/data/haarcascades you can use different available xml files as per your need. The live_face_detection.py is main file and has all code for face and eye detection. Have uploaded some of captured images which are faces and eyes detected in live video frame from camera. The name of taken images is stored into mysql database with time stamp.

Required packages installation:

pip3 install opencv-python

pip3 install MySQL-connector-python

pip3 install cmake

pip3 install dlib

pip3 install face-recognition

pip3 install sendgrid

pip3 install pyttsx3

pip3 install PyAudio

apt install espeak

apt install jackd2
