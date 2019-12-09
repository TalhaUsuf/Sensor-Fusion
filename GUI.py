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
detections_f = [] # final fusion detections.
detections_b = [] # blind detections (no camera).

cap = cv2.VideoCapture(1)
cap.set(3,1280)
cap.set(4,720)

context = zmq.Context()

#  Socket to talk to server
print("Connecting to fusion engine")
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

print("Entering GUI Loop...")

camera_radar_fusion_enabled = True
camera_lidar_fusion_enabled = True
blind_RadarLidar_fusion_enabled = True
camRadar_score_threshold = 0
camLidar_score_threshold = 0
blind_score_threshold = 0
tol_additional = 0 		#tolerance in addition to radar/lidar radius, for fusion.

def comms_thread():
	global detections_c, detections_l, detections_r, detections_f, detections_b, mutex, radar_font

	while True:
		message = socket.recv_string()
		socket.send(b"world")
		
		detections_r.clear()
		detections_c.clear()
		detections_l.clear()
		detections_f.clear()
		detections_b.clear()
		
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
	
	raw_frame= frame.copy()
	raw_frame= cv2.putText(raw_frame,'PRE-FUSION',(135,50), radar_font, 1,(204, 0, 204),2,cv2.LINE_AA)
	frame= cv2.putText(frame,'POST-FUSION',(75,50), radar_font, 1,(255,255,0),2,cv2.LINE_AA)

	mutex.acquire()

	
	#print("gui drawing", detections_c)

	for i in detections_c:
		raw_frame = cv2.rectangle(raw_frame, (i[0], i[1]), (i[2], i[3]), (0,255,0), 2)
		camera_radar_score = 0
		camera_lidar_score = 0

		#check for overlapping radar points.
		if camera_radar_fusion_enabled:

			for j in detections_r:
				# radar_fusion_tolerance = radius + constant.
				tol = j[3] + tol_additional
				#check for radar-camera intersection.
				if ((j[0] > i[0] - tol) and (j[0] < i[2] + tol) and (j[1] > i[1] - tol) and (j[1] < i[3] + tol)):
					camera_radar_score += 10
					
		#check for overlapping lidar points.
		if camera_lidar_fusion_enabled:

			for j in detections_l:
				# lidar_fusion_tolerance = radius + constant.
				tol = j[3] + tol_additional
				#check for camera-lidar intersection.
				if ((j[0] > i[0] - tol) and (j[0] < i[2] + tol) and (j[1] > i[1] - tol) and (j[1] < i[3] + tol)):
					camera_lidar_score += 4

		
		#add to fusion buffer if we have enough score.
		#if ( (camera_radar_score > camRadar_score_threshold) and (camera_lidar_score > camLidar_score_threshold) ):
		detections_f.append([i[0], i[1], i[2], i[3], camera_radar_score, camera_lidar_score])
					
	for i in detections_r:
		blind_lidar_score = 0
		if ( len(detections_c) < 1 ):
			# No camera detection, it could be dark.
			if (blind_RadarLidar_fusion_enabled):
				for j in detections_l:
					# lidar_fusion_tolerance = 2xradiusRadar + constant.
					tol = 2*i[3] + tol_additional
					#check for radar-lidar intersection.
					if ( (j[0] < i[0] + tol) and (j[1] < i[1] + tol) ):
						blind_lidar_score += 50

			if (blind_lidar_score > blind_score_threshold):
				#Approxiate a bounding box close to human size.
				rect_width  = 170 - i[2]/5
				rect_height = 400 - i[2]/20
				px1 = i[0] - int(rect_width/2)
				py1 = i[1] - int(rect_height/2) 
				px2 = i[0] + int(rect_width/2)
				py2 = i[1] + int(rect_height/2)
				detections_b.append([px1, py1, px2, py2, blind_lidar_score])

		raw_frame=cv2.circle(raw_frame,(i[0], i[1]), i[3],(204, 0, 204),10)
		modf_frame=cv2.putText(modf_frame,str(i[2])+"m",(i[0]+15,i[1]-50), radar_font, 1,(0, 255, 255),2,cv2.LINE_AA)
	
	for i in detections_l:
		raw_frame=cv2.circle(raw_frame,(i[0], i[1]), i[3],(0, 191, 255),3)

	#display contents from fusion buffer.
	for i in detections_f:
		modf_frame = cv2.rectangle(modf_frame, (i[0], i[1]), (i[2], i[3]), (255,255,0), 2)
		modf_frame = cv2.putText(modf_frame,"Radar-score = " + str(i[4]),(i[0],i[3]+10), radar_font, 1,(255,255,0),2,cv2.LINE_AA)
		modf_frame = cv2.putText(modf_frame,"Lidar-score = " + str(i[5]),(i[0],i[3]+40), radar_font, 1,(255,255,0),2,cv2.LINE_AA)

	#display contents from blind Radar/Lidar Fusion.
	for i in detections_b:
		modf_frame = cv2.rectangle(modf_frame, (i[0], i[1]), (i[2], i[3]), (203,192,255), 2)
		modf_frame = cv2.putText(modf_frame,"Blind-score = " + str(i[4]),(i[0],i[3]+10), radar_font, 1,(203,192,255),2,cv2.LINE_AA)


	mutex.release()

	# create side by side displays, with fusion(left) and without fusion(right).
	numpy_horizontal = np.hstack((modf_frame, raw_frame))
	shortened = cv2.resize(numpy_horizontal, (0, 0), None, .5, .5)
	
	cv2.imshow('frame',shortened)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break