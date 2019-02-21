import time
import zmq
import subprocess
import _thread
import datetime
from threading import Lock

import _pickle as pickle
import numpy as np
import math
import mkmath as mk
import cv2

PORT_CAMERA = "5555"
PORT_LIDAR = "5556"
PORT_RADAR = "5557"
PORT_GUI = "5558"

radar_data = list()
camera_data = list()
lidar_data = list()

camera_data_mutex = Lock()
radar_data_mutex = Lock()
lidar_data_mutex = Lock()

turn = True

#Rotation and Translation Matrices

#Lidar
RT_lidar=np.matrix('0 1 0 0;0 0 1 0.05;1 0 0 -0.06')
#Radar 
RT=np.matrix('1 0 0 0.05;0 0 -1 -0.06;0 1 0 -0.05')

fy=1084
fx=1089
cx=640
cy=360
Sx=16/9
Sy=1


#pixel buffer for radar
radar_pixel=[]
#pixel buffer for lidar
lidar_pixel=[]


def thread_camera():
	
	global turn
	
	while True:
		
		
		#  Wait for next request from client
		message_camera = socket_camera.recv()
		
		#parse camera data
		if (~turn):
			#print("detectnetmessage received...")
			camera_data_mutex.acquire()
			camera_data.clear()
			while len(message_camera)>19:
				px1 = int(message_camera[0:4])
				py1 = int(message_camera[4:8])
				px2 = int(message_camera[8:12])
				py2 = int(message_camera[12:16])
				#print("Fusion: ",px1," ",py1," ",px2," ",py2)
				camera_certainty = float(message_camera[16:20])/10000
				camera_data.append((px1, py1, px2, py2, camera_certainty))
				message_camera = message_camera[20:]
		
			
			while (len(camera_data)>=10):
				del camera_data[0]	
				
			socket_camera.send(b"Ack_Cam")
			
			camera_data_mutex.release()
			turn=True
	
def thread_radar():
	while(True):  
	#Blocking receive
		message = socket_radar.recv()
		socket_radar.send(b"200")
		
		radar_data.clear()
		
		#calculation of loop params	
		number_of_obj= (len(message)-1)/15
		#print("Number of detected Objects:")
		#print(number_of_obj)
		#counters	
		count=0
		#position on string
		index=0 
	
		while(count<number_of_obj):
			
			#print("Entered loop no",count)
			x = int(message[index:index+4+1])/100
			y = int(message[index+5:index+9+1])/100
			z = int(message[index+10:index+14+1])/100
			#print("Radar xyz=  : ",x," ",y," ",z)
			#calculating radius for scaling circle radius
			r = math.sqrt(math.pow(x,2)+math.pow(y,2)+pow(z,2))
			index = index+15
			count = count+1
			
			#radius
			"""rad=10
			if(r<1):
				rad=20
			elif(r>10):
				rad=5
			else:
				rad=5+15/9*r"""
				
			#SCALING THE CIRCLES
			distance= r/1000
			#CIRCLE WIDTH
			circle_radius=5
			if(distance>=12):
				circle_radius=5
			elif(distance<0.5):
				circle_radius=100
			else:
				circle_radius= int(100-8.3*distance)
			
			#pixel conversion===========================
			
			#old method
			#uv= mk.convertWorldCordsToPixelsRadar(x,y,z,fx,fy,cx,cy,RT,Sx,Sy)
			
			#new method
			uv=mk.LidToPixels(x,y,z,RT,fx,fy,Sx,Sy,cx,cy)
			uv.append(circle_radius)
			
			
			radar_data.append(uv)
			
		#resetting loop params	
		index=0
		count=0
		
"""LIDAR"""
		
def thread_lidar():
	while(True): 
	
		message = socket_lidar.recv()
		#print("Received lidar scan")
		socket_lidar.send(b"200")
		lidar_data.clear()
		payload=pickle.loads(message)
		#print("Lidar Msg:",payload)
		
		for cursor in payload:

			cartesian= mk.convertToCartesian(cursor[2]/1000,cursor[1])
			x= (cartesian["x"])
			y= (cartesian["y"])
		   
			if(cursor[2]<12000 and((cursor[1]>329 and cursor[1]<361)or((cursor[1]>=0 and cursor[1]<31)))):

				uv=mk.LidToPixels(x,y,0,RT_lidar,fx,fy,Sx,Sy,cx,cy)

				#SCALING THE CIRCLES
				distance= cursor[2]/1000
				#CIRCLE WIDTH
				circle_radius=5
				if(distance>=12):
					circle_radius=5
				elif(distance<0.5):
					circle_radius=100
				else:
					circle_radius= int(100-8.3*distance)

				uv.append(circle_radius)
				lidar_data.append(uv)
				
#end lidar thread
		
		
		
		
		
	

#############################################
########## INITALIZATION ###################
###########################################

#create camera vision socket
context_camera = zmq.Context()
socket_camera = context_camera.socket(zmq.REP)
socket_camera.bind("tcp://*:" + PORT_CAMERA)

#create radar socket
context_radar = zmq.Context()
socket_radar = context_radar.socket(zmq.REP)
socket_radar.bind("tcp://*:" + PORT_RADAR)

#create lidar socket
context_lidar = zmq.Context()
socket_lidar = context_lidar.socket(zmq.REP)
socket_lidar.bind("tcp://*:"+PORT_LIDAR)


print("Initializing Camera Feed...")
pid_camera = subprocess.Popen(["/home/nvidia/jetson-inference/jetson-inference/build/aarch64/bin//detectnet-camera", "pednet"])
print("Configuring Radar to start producing data...")
pid_radar_config = subprocess.Popen(["/home/nvidia/Documents/radar_cfgs/reader_writer"])
print("Starting Radar incoming data parser ")
pid_radar_data = subprocess.Popen(["/home/nvidia/Documents/radar_cfgs/dataport_reader_zmq"])
print("Starting Lidar Executable")
pid_lidar_data= subprocess.Popen(["python3","/home/nvidia/Documents/ADAS/lidar.py"])

print("Starting GUI...")
pid_GUI = subprocess.Popen(["python3", "/home/nvidia/Documents/ADAS/GUI.py"])

#create GUI socket
context_gui = zmq.Context()
socket_gui = context_gui.socket(zmq.REQ)
socket_gui.connect("tcp://localhost:" + PORT_GUI)	

#############################################
########## END INITALIZATION ###################
###########################################


try: 
	_thread.start_new_thread(thread_camera, ())
	_thread.start_new_thread(thread_radar, ())
	_thread.start_new_thread(thread_lidar, ())
except:
	print("Error: Unable to start thread")
	
print("Entering loop")

while 1:
	
	if(turn):
		camera_data_mutex.acquire()
		camera_buffer = ""
		for x1, y1, x2, y2, cert in camera_data:
			#camera_buffer += "{0:04d}%{1:04d}%{2:04d}%{3:04d}%{4:5.3f}|".format(x1, y1, x2, y2, cert)
			camera_buffer += "{0:04d}{1:04d}{2:04d}{3:04d}{4:5.3f}".format(x1, y1, x2, y2, cert)
			#cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3) 
			#print(x1, y1, x2, y2, e)
		
		#print("Radar Data")
		radar_buffer = ""
		#FIX THIS: radar_data is not in x,y,z
		#for x, y, z in radar_data:
		for u, v, w, x in radar_data:
			#radar_buffer += "{0:03d}{1:03d}{2:03d}".format(x, y, z)
			#radar_buffer += "{0:d}%{1:d}|".format(u, v)
			#print(u)
			#print(v)
			if (u <=1280 and u>=0 and v<=720 and v>=0):
				radar_buffer += "{0:04d}{1:04d}{2:04d}".format(u, v, x)
			#cv2.circle(frame, (x, y), 40, (0, 0, 255), 3)
			#print(x, y, z)
			#fusion algorithm
		
		
		#radar_buffer = radar_buffer[:-1]
		'''LIDAR MUJAHEED'''
		lidar_buffer=""
		for u, v, w, x in lidar_data:
			if (u <=1280 and u>=0 and v<=720 and v>=0):
				lidar_buffer += "{0:04d}{1:04d}{2:04d}".format(u, v, x)
		
		
		
		
		'''LIDAR MUJAHEED END'''
		#print("==========")
		
		#crafting a single message to send to GUI, using '/' delimiters.
		#print("sending to gui...", camera_buffer)
		fusion_message = "{}/{}/{}".format(camera_buffer, radar_buffer, lidar_buffer)
		socket_gui.send_string(fusion_message)
		gui_message = socket_gui.recv()
		#print("Received reply")
		
		
		camera_data_mutex.release()
		
		turn = False
	
	
	pass






#########################################
############ HELPER FUNCTIONS ###########
#########################################





 
    
