import cv2
import time
import datetime

# getting face and eye cascade classifier
face_cascade = cv2.CascadeClassifier("cascade_lib/data/haarcascades/haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("cascade_lib/data/haarcascades/haarcascade_eye.xml")

# initialise video read object
cap = cv2.VideoCapture(0)

while (cap.isOpened()):
	ret, frame = cap.read() # reading frame from video source
	gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert into gray scale image

	# getting face bounding rectangle values
	faces = face_cascade.detectMultiScale(gray_frame,scaleFactor=1.05,minNeighbors=3)
	for (x,y,w,h) in faces:
		frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

		roi_gray = gray_frame[y:y+h, x:x+w] # getting region of interest from gray frame, read by camera
		roi_color = frame[y:y+h, x:x+w] # getting region of interest from color frame, read by camera
		curr_time = str(datetime.datetime.now())
		cv2.imwrite('face_roi_'+curr_time+'.jpg', roi_color) # take snaps and save for detected faces

		# geetting eye bounding rectangle values
		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex,ey,ew,eh) in eyes:
			cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,0,255), 2)
	cv2.imshow('FaceDetect',frame)
	k = cv2.waitKey(10)
	if k==27:
		break

cap.release()
cv2.destroyAllWindows()
