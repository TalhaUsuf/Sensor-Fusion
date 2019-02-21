import numpy as np
import cv2
import zmq
import _thread
from threading import Lock

mutex = Lock()

pxpy = []
rectangles = []


cap = cv2.VideoCapture(1)

context = zmq.Context()

#  Socket to talk to server
print("Connecting to fusion engine")
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

print("Entering GUI Loop...")

def comms_thread():
	while True:
		message = socket.recv_string()
		
		pxpy.clear()
		rectangles.clear()
		
		mutex.acquire()
		
		data = message.split('/')
		camera_data = data[0]
		radar_data = data[1]
		lidar_data = data[2]
		socket.send(b"world")
			
		camera_data_array = camera_data.split('|')
		for xyc in camera_data_array:
			rectangles.append(xyc.split('%'))
			
		radar_data_array = radar_data.split('|')
		for uv in radar_data_array:
			pxpy.append(uv.split('%'))
			
		print(camera_data)
		print(rectangles)
			
		mutex.release()
		
'''	
try: 
	_thread.start_new_thread(comms_thread, ())
	pass
except:
	print("Error: Unable to start thread")	
'''
	
while(True):
	
	
	message = socket.recv_string()
	data = message.split('/')
	camera_data = data[0]
	radar_data = data[1]
	lidar_data = data[2]
	#print(data)
	print(camera_data)
	print(radar_data)
	print(lidar_data)
	print("-----------------------")
	socket.send(b"world")
	ret, frame = cap.read()
	
	modf_frame = frame
	
	
	
	
	#breakdown the aggregated camera_data into individual rectangles, then draw rectangles on the frame. 
	while len(camera_data)>20:
		px1 = int(camera_data[0:4])
		py1 = int(camera_data[4:8])
		px2 = int(camera_data[8:12])
		py2 = int(camera_data[12:16])
		camera_certainty = float(camera_data[16:21])
		camera_data = camera_data[21:]
		modf_frame = cv2.rectangle(modf_frame, (px1, py1), (px2, py2), (0,255,0), 2)
	
	#breakdown the aggregated camera_data into individual rectangles, then draw rectangles on the frame. 
	while len(radar_data)>7:
		px = int(radar_data[0:4])
		py = int(radar_data[4:8])
		radar_data = radar_data[8:]
		modf_frame = cv2.rectangle(modf_frame, (px, py), (px+10, py+10), (0,0,255), 2)
	
	#lidar	
	while len(lidar_data)>7:
		px = int(lidar_data[0:4])
		py = int(lidar_data[4:8])
		circle_radius=int(lidar_data[8:12])
		lidar_data = lidar_data[12:]
		modf_frame=cv2.circle(modf_frame,(px, py),circle_radius,(0, 191, 255),1)

	
	'''
	radar_data_array = radar_data.split('|')
	print(radar_data_array)
	for uv in radar_data_array:
		print(uv)
		pxpy = uv.split('%')
		print(pxpy)
		if len(pxpy)==2:
			modf_frame = cv2.rectangle(modf_frame, (int(pxpy[0]), int(pxpy[1])), (int(pxpy[0])+10, int(pxpy[1])+10), (0,0,255), 2)
'''
	
	'''
	ret, frame = cap.read()
	
	modf_frame = frame
	
	mutex.acquire()
	
	for item in pxpy:
		if(len(item)==2):
			modf_frame = cv2.rectangle(modf_frame, (int(item[0]), int(item[1])), (int(item[0])+10, int(item[1])+10), (0,0,255), 2)
			
	for item in rectangles:
		if(len(item) == 5):
			modf_frame = cv2.rectangle(modf_frame, (item[0], item[1]), (item[2], item[3]), (0,255,0), 2)
	
	mutex.release()
	
	'''
	
	
	cv2.imshow('frame',modf_frame)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	
