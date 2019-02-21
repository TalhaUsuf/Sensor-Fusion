import numpy as np
import cv2
import zmq
import _thread
from threading import Lock

mutex = Lock()

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
	global detections_c, detections_l, detections_r, mutex


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
			
		#breakdown the aggregated camera_data into individual rectangles, then draw rectangles on the frame. 
		while len(radar_data)>7:
			px = int(radar_data[0:4])
			py = int(radar_data[4:8])
			radar_circle=int(radar_data[8:12])
			radar_data = radar_data[12:]
			detections_r.append([px, py,radar_circle])
			new_radar = True

		#lidar	
		while len(lidar_data)>7:
			px = int(lidar_data[0:4])
			py = int(lidar_data[4:8])
			circle_radius=int(lidar_data[8:12])
			lidar_data = lidar_data[12:]
			detections_l.append([px, py, circle_radius])

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
		modf_frame=cv2.circle(modf_frame,(i[0], i[1]), i[2],(204, 0, 204),2)
		
	for i in detections_l:
		modf_frame=cv2.circle(modf_frame,(i[0], i[1]), i[2],(0, 191, 255),1)

		
	mutex.release()

	cv2.imshow('frame',modf_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
