import numpy as np
import cv2
import zmq
import _thread
from threading import Lock

mutex = Lock()
radar_font = cv2.FONT_HERSHEY_SIMPLEX

detections_r = []
detections_c = []
detections_l = []

cap = cv2.VideoCapture(4)
cap.set(3,1280);
cap.set(4,720);


context = zmq.Context()

#  Socket to talk to server
print("Connecting to fusion engine")
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

print("Entering GUI Loop...")

def comms_thread():
	global detections_c, detections_l, detections_r, mutex, radar_font


	while True:
		message = socket.recv_string()
		socket.send(b"world")
		
		detections_r.clear()
		detections_c.clear()
		detections_l.clear()
		
		mutex.acquire()
		
		data = message.split('/')
		camera_data = data[0]
		#print("gui receive ", camera_data)
		radar_data = data[1]
		lidar_data = data[2]

			#breakdown the aggregated camera_data into individual rectangles, then draw rectangles on the frame. 
		while len(camera_data)>20:
			px1 = int(camera_data[0:4])
			py1 = int(camera_data[4:8])
			px2 = int(camera_data[8:12])
			py2 = int(camera_data[12:16])
			#camera_certainty = float(camera_data[16:21])
			camera_data = camera_data[21:]
			detections_c.append([px1, py1, px2, py2])
			
		#breakdown the aggregated radar_data into individual rectangles, then draw rectangles on the frame. 
		while len(radar_data)>7:
			px = int(radar_data[0:4])
			py = int(radar_data[4:8])
			distance=int(radar_data[8:12])
			radar_data = radar_data[12:]
			
			#converting back to meters.
			distance /= 100
			#print("radar distance is:  ", distance, " meters")
			
			radar_circle=5
			if(distance>=12):
				radar_circle=5
			elif(distance<0.5):
				radar_circle=70
			else:
				radar_circle= int(70-5.65*distance)
				
			detections_r.append([px, py,distance, radar_circle])
			new_radar = True

		#lidar	
		while len(lidar_data)>7:
			px = int(lidar_data[0:4])
			py = int(lidar_data[4:8])
			distance=int(lidar_data[8:12])
			lidar_data = lidar_data[12:]
			
			#CIRCLE WIDTH
			circle_radius=5
			if(distance>=12):
				circle_radius=5
			elif(distance<0.5):
				circle_radius=70
			else:
				circle_radius= int(70-5.65*distance)
			
			detections_l.append([px, py, distance, circle_radius])

		mutex.release()
		
try: 
	_thread.start_new_thread(comms_thread, ())
except:
	print("Error: Unable to start thread")	

while(True):
	ret, frame = cap.read()
	modf_frame = frame
	
	mutex.acquire()
	
	#print("gui drawing", detections_c)

	for i in detections_c:
		modf_frame = cv2.rectangle(modf_frame, (i[0], i[1]), (i[2], i[3]), (0,255,0), 2)
		
	for i in detections_r:
		modf_frame=cv2.circle(modf_frame,(i[0], i[1]), i[3],(204, 0, 204),3)
		modf_frame=cv2.putText(modf_frame,str(i[2])+"m",(i[0]+15,i[1]-50), radar_font, 3,(0, 255, 255),2,cv2.LINE_AA)
	
	for i in detections_l:
		modf_frame=cv2.circle(modf_frame,(i[0], i[1]), i[3],(0, 191, 255),3)

		
	mutex.release()

	cv2.imshow('frame',modf_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
