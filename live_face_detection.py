import cv2
import time
import datetime
import mysql.connector
import uuid
import face_recognition
import time
import os

# sample known images of employee to recognise person
known_images = ['Kushal.jpg','Ankit.jpg']

cmp_picture = face_recognition.load_image_file("sachin.jpg")
cmp_encoding = face_recognition.face_encodings(cmp_picture)[0]

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="asterisk",
  database="raspbery_pi"
)

mycursor = mydb.cursor()

# getting face and eye cascade classifier
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")

# initialise video read object
cap = cv2.VideoCapture(0)
print(cap.get(cv2.CAP_PROP_FPS))
cap.set(cv2.CAP_PROP_FPS, 10)
print(cap.get(cv2.CAP_PROP_FPS))

while (cap.isOpened()):
	#time.sleep(1)
	ret, frame = cap.read() # reading frame from video source
	gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert into gray scale image

	# getting face bounding rectangle values
	faces = face_cascade.detectMultiScale(gray_frame,scaleFactor=1.05,minNeighbors=3)
	for (x,y,w,h) in faces:
		frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

		roi_gray = gray_frame[y:y+h, x:x+w] # getting region of interest from gray frame, read by camera
		roi_color = frame[y:y+h, x:x+w] # getting region of interest from color frame, read by camera
		curr_time = str(datetime.datetime.now())
		#cv2.imwrite('face_roi_'+curr_time+'.jpg', roi_color) # take snaps and save for detected faces

		# geetting eye bounding rectangle values
		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex,ey,ew,eh) in eyes:
			#cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,0,255), 2)
			temp_img_name = str(uuid.uuid4())+".jpg"

			rgb_frame = cv2.cvtColor(roi_color, cv2.COLOR_BGR2RGB)
			check_img_name = str(uuid.uuid4())+".jpg"
			cv2.imwrite(check_img_name, rgb_frame)

			frame_picture = face_recognition.load_image_file(check_img_name)
			frame_encoding = face_recognition.face_encodings(frame_picture)
			os.system('rm '+check_img_name)
			if len(frame_encoding) > 0:
				frame_encoding = face_recognition.face_encodings(frame_picture)[0]
				results = face_recognition.compare_faces([frame_encoding], cmp_encoding)
				cmp_encoding = frame_encoding
				if results[0] == True:
					print("same face detected")
				else:
					print("new face detected")
					cv2.imwrite(temp_img_name, roi_color)
					detection_flag = 0

					# recognising the face with help of previously stored images
					for img in known_images:
						print("inside checking person")
						temp_img = face_recognition.load_image_file(img)
						known_image_encoding = face_recognition.face_encodings(temp_img)[0]
						results = face_recognition.compare_faces([known_image_encoding], frame_encoding)

						if results[0] == True:
							detection_flag = 1
							face_identify = img.split('.')[0] # getting name of image, the recognised person
							detected_output = "It's a picture of "+face_identify
							font = cv2.FONT_HERSHEY_SIMPLEX
							cv2.putText(frame, face_identify, (10,100), font, 1, (0,255,255), 2, cv2.LINE_AA)
						else:
							unknown_face_identify = "Unknown"
							not_detected_output = "It is unknown picture!"
							#font = cv2.FONT_HERSHEY_SIMPLEX
							#cv2.putText(frame, unknown_face_identify, (10,100), font, 1, (0,255,255), 2, cv2.LINE_AA)

					if detection_flag == 1:
						print(detected_output)
						sql = "INSERT INTO image (image_name,person_detected,event_time) VALUES (%s,%s,%s)"
						val = (temp_img_name,face_identify,curr_time)
						mycursor.execute(sql, val)
						mydb.commit()
					else:
						print(not_detected_output)
						sql = "INSERT INTO image (image_name,person_detected,event_time) VALUES (%s,%s,%s)"
						val = (temp_img_name,unknown_face_identify,curr_time)
						mycursor.execute(sql, val)
						mydb.commit()

			else:
				print("no face detected")

			

	cv2.imshow('FaceDetect',frame)
	k = cv2.waitKey(10)
	if k==27:
		break

cap.release()
cv2.destroyAllWindows()
