#imports
from rplidar import RPLidar
import zmq
import _pickle as pickle

#socket
context = zmq.Context()
print("Lidar Executable: Connecting to Fusion Engine…")
socket = context.socket(zmq.REQ)
print("Connection Status:",socket.connect("tcp://localhost:5556"))

#lidar initialization
lidar = RPLidar('/dev/ttyUSB0')

#diagnostics
info = lidar.get_info()
print(info)
health = lidar.get_health()
print(health)

scan_FOV=[]

for i, scan in enumerate(lidar.iter_scans()):
	print('%d: Got %d measurments' % (i, len(scan)))
	print("Sending Scan")
	scan_FOV.clear()
    
	for cursor in scan:
		if(((cursor[1]>329 and cursor[1]<361)or((cursor[1]>=0 and cursor[1]<31)))):
			scan_FOV.append(cursor)
			#print(scan_FOV)
			
	if (len(scan_FOV)!=0):
		socket.send(pickle.dumps(scan_FOV))

		#  Get the reply.
		message = socket.recv()
		print("Received reply: %s"%message)
    
    #print(scan)
    #if i > 1000:
       # break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
