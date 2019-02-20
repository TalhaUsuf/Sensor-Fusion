#import
import numpy as np
import math
import mkmath as mk
import cv2
import time
import zmq
import _pickle as pickle

#camera index in /dev/video<index>
camera_devindex = 1

#havent used but left
MIN_RADAR_DATA_LENGTH = 15 + 1 #X,Y,Z + '\0'


#IPC initialization
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

#meant for scaling circles around dots
cw=100


#camera parms
#RT=np.matrix('0 0 1 0;1 0 0 0.05;0 1 0 0.05;0 0 0 1') #obsolete now
RT=np.matrix('1 0 0 0;0 0 1 0;0 1 0 0;0 0 0 1') #based on corrected axes
fy=863.1305
fx=882.0941
cx=980
cy=330
Sx=4
Sy=3

#pixel buffer for radar
radar_pixel=[]

#radar_data not used but left for future
radar_data=[]
radar_cursor=[]

#start capture
cap = cv2.VideoCapture(camera_devindex)

#while loop to do radar+camera fusion
while(True):
    # Capture frame-by-frame
	ret, frame = cap.read()
	print("Entered while loop")
   
	#Blocking receive
	message = socket.recv()
	print("Message received")
	print(message)
	socket.send(b"200")
		
	#calculation of loop params	
	length_payload=len(message)-1
	number_of_obj= length_payload/15
	print("Number of detected Objects:")
	print(number_of_obj)
	
	#counters	
	count=0
	#position on string
	index=0 
	
	while(count<number_of_obj):
		
		print("Entered loop no",count)
		x = int(message[index:index+4+1])
		x= x/100
		y = int(message[index+5:index+9+1])
		y=y/100
		z = int(message[index+10:index+14+1])
		z=z/100
		
		#calculating radius for scaling circle radius
		r = math.sqrt(math.pow(x,2)+math.pow(y,2)+pow(z,2))
		print("Radius:", r)
		print(x," ",y," ",z)
		index= index+15
		count= count+1
		
		
		#radius
		rad=10
		if(r<1):
			rad=20
		elif(r>10):
			rad=5
		else:
			rad=5+15/9*r
		
		
		#pixel conversion===========================================================
		
		#old method
		#uv= mk.convertWorldCordsToPixelsRadar(x,y,z,fx,fy,cx,cy,RT,Sx,Sy)
		
		#new method
		uv= convertWithoutRT(U,fx,fy,cx,cy,Sx,Sy)
		
		
		#appending lidar 
		radar_pixel.append(uv)
		
		print("Calculated pixel coords")
		print(uv)
		
		#drawing circle on image with scaled radius 
		circle=cv2.circle(frame,(uv[0], uv[1]),int(cw/r),(255,0,0),0)
	
	#resetting loop params	
	index=0
	count=0
	
	#resetting lidar buffer
	radar_pixel.clear()
	
	#show frame and then go back
	cv2.imshow('frame',circle)
	if cv2.waitKey(100) & 0xFF == ord('q'):
		break
	
		
	
#we are done. release camera and destroy windows
cap.release()
cv2.destroyAllWindows()
