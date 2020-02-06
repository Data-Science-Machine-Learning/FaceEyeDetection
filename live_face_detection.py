import cv2
import numpy as np
import time
import datetime
import mysql.connector
import uuid
import face_recognition
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import constant as ct
import pyttsx3

from_email='ankit.jayswal@samcomtechnologies.com'
to_emails='ankitjayswal87@gmail.com'
subject='Person Detected - '
html_content='<strong>This is notification for person detection, it is system generated mail.</strong>'

def send_mail(from_email,to_emails,subject,html_content):
	message = Mail(from_email=from_email,to_emails=to_emails,subject=subject,html_content=html_content)
	try:
    		sg = SendGridAPIClient(ct.SENDGRID)
    		response = sg.send(message)
    		print(response.status_code)
    		#print(response.body)
    		#print(response.headers)
	except Exception as e:
    		print(str(e))

face_identify = ""

#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#video_file_name = str(uuid.uuid4())+".avi"
#out = cv2.VideoWriter(video_file_name, fourcc, 20.0, (640,480))
#os.system('chmod 777 '+video_file_name)

# sample known images of employee to recognise person
known_images = ['Ankit.jpg','Kushal.jpg','Prashant.jpg','Parth.jpg','Maksud.jpg']

# list of known image ecodings
known_encodings = []

# adding all known face encodings
for img in known_images:
	temp_img = face_recognition.load_image_file(img)
	temp_encoding = face_recognition.face_encodings(temp_img)[0]
	known_encodings.append(temp_encoding)

# initial encodings to compare
cmp_picture = face_recognition.load_image_file(ct.INITIALIMAGE)
cmp_encoding = face_recognition.face_encodings(cmp_picture)[0]

# mysql connection
mydb = mysql.connector.connect(
  host=ct.HOST,
  user=ct.DBUSER,
  passwd=ct.DBPASSWORD,
  database=ct.DATABASE
)

mycursor = mydb.cursor()

# getting face and eye cascade classifier
face_cascade = cv2.CascadeClassifier(ct.FACECASCADE)
eye_cascade = cv2.CascadeClassifier(ct.EYESCASCADE)

# initialise video read object
cap = cv2.VideoCapture(0)
print(cap.get(cv2.CAP_PROP_FPS))
#cap.set(cv2.CAP_PROP_FPS, 10)
#print(cap.get(cv2.CAP_PROP_FPS))

while (cap.isOpened()):
	#time.sleep(1)
	ret, frame = cap.read() # reading frame from video source
	gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert into gray scale image
	#out.write(frame)

	# getting face bounding rectangle values
	faces = face_cascade.detectMultiScale(gray_frame,scaleFactor=1.05,minNeighbors=3)
	for (x,y,w,h) in faces:
		# checking area of face bounding rect
		#area = w*h
		#print("Area: "+str(area))
		#if area <= ct.FACEDETECTIONAREA:
			#continue;
		frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

		roi_gray = gray_frame[y:y+h, x:x+w] # getting region of interest from gray frame, read by camera
		roi_color = frame[y:y+h, x:x+w] # getting region of interest from color frame, read by camera
		curr_time = str(datetime.datetime.now())
		#cv2.imwrite('face_roi_'+curr_time+'.jpg', roi_color) # take snaps and save for detected faces

		# getting eye bounding rectangle values
		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex,ey,ew,eh) in eyes:
			#cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,0,255), 2)
			temp_img_name = str(uuid.uuid4())+".jpg"

			# need to convert into RGB to process in face recognise
			roi_color_resize = cv2.resize(roi_color, (0, 0), fx=0.25, fy=0.25)
			rgb_frame = cv2.cvtColor(roi_color_resize, cv2.COLOR_BGR2RGB)
			check_img_name = str(uuid.uuid4())+".jpg"
			cv2.imwrite(check_img_name, rgb_frame)

			frame_picture = face_recognition.load_image_file(check_img_name)
			frame_encoding = face_recognition.face_encodings(frame_picture)
			os.system('rm '+check_img_name)
			# some face bounding detected
			if len(frame_encoding) > 0:
				frame_encoding = face_recognition.face_encodings(frame_picture)[0]
				results = face_recognition.compare_faces([frame_encoding], cmp_encoding)
				cmp_encoding = frame_encoding
				if results[0] == True:
					print("same face detected")
					font = cv2.FONT_HERSHEY_SIMPLEX
					cv2.putText(frame, face_identify, (10,100), font, 1, (0,255,255), 2, cv2.LINE_AA)
				else:
					print("new face detected")
					cv2.imwrite(temp_img_name, roi_color)
					detection_flag = 0

					# recognising the face with help of previously stored images
					matches = face_recognition.compare_faces(known_encodings, frame_encoding)
					if True in matches:
						detection_flag = 1
						face_distances = face_recognition.face_distance(known_encodings, frame_encoding)
						best_match_index = np.argmin(face_distances)
						print(known_images[best_match_index])
						face_identify = known_images[best_match_index].split('.')[0] # the recognised person
						detected_output = "It's a picture of "+face_identify
						font = cv2.FONT_HERSHEY_SIMPLEX
						cv2.putText(frame, face_identify, (10,100), font, 1, (0,255,255), 2, cv2.LINE_AA)
					else:
						unknown_face_identify = "Unknown"
						not_detected_output = "It is unknown picture!"

					if detection_flag == 1:
						print(detected_output)
						sql = "INSERT INTO image (image_name,person_detected,event_time) VALUES (%s,%s,%s)"
						val = (temp_img_name,face_identify,curr_time)
						mycursor.execute(sql, val)
						mydb.commit()
						# playing thank you
						file = "thankyou.mp3"
						os.system("mpg123 " + file)
						# playing name also after thank you
						engine = pyttsx3.init()
						engine.setProperty('rate', 110)
						engine.say(face_identify)
						engine.runAndWait()
						engine.stop()

						person_subject = subject+" "+str(face_identify)
						#send_mail(from_email,to_emails,person_subject,html_content)
					else:
						print(not_detected_output)
						sql = "INSERT INTO image (image_name,person_detected,event_time) VALUES (%s,%s,%s)"
						val = (temp_img_name,unknown_face_identify,curr_time)
						mycursor.execute(sql, val)
						mydb.commit()

			else:
				print("no face detected")
				font = cv2.FONT_HERSHEY_SIMPLEX
				no_face = "No Face Detected"
				cv2.putText(frame, no_face, (10,100), font, 1, (0,255,255), 2, cv2.LINE_AA)

			

	cv2.imshow('FaceDetect',frame)
	k = cv2.waitKey(10)
	if k==27:
		break

cap.release()
#out.release()
cv2.destroyAllWindows()
