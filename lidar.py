#imports
from rplidar import RPLidar
import zmq
import _pickle as pickle
import numpy as np  
from sklearn.cluster import KMeans 

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
		
		np_scan= np.array(scan_FOV)
		scan_kmeans=KMeans()
		kmeans_scan_obj=scan_kmeans.fit(np_scan)
		min_scan=kmeans_scan_obj.cluster_centers_
		
		print("Clustered Scan: ",min_scan)
		socket.send(pickle.dumps(min_scan))

		#  Get the reply.
		message = socket.recv()
		print("Received reply: %s"%message)
    
    #print(scan)
    #if i > 1000:
       # break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
