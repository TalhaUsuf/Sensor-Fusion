#imports
from rplidar import RPLidar
import zmq
import _pickle as pickle
import numpy as np  
from sklearn.cluster import KMeans 
import time

#socket
context = zmq.Context()
print("Lidar Executable: Connecting to Fusion Engine…")
socket = context.socket(zmq.REQ)
print("Connection Status:",socket.connect("tcp://localhost:5556"))

#lidar initialization
lidar = RPLidar('/dev/ttyUSB0')





lidar.reset()

#diagnostics
while(True):

	try:
		info = lidar.get_info()
		print(info)
		health = lidar.get_health()
		print(health)

		scan_FOV=[]
		scan_gen= lidar.iter_scans()
		#print("Past iter_Scans")
		

		for i, scan in enumerate(scan_gen):
			#print("I am in the loop")
			
			#print('%d: Got %d measurments' % (i, len(scan)))
			#print("Sending Scan")
			scan_FOV.clear()
			n_clusters=10
			
			for cursor in scan:
				if(((cursor[1]>329 and cursor[1]<361)or((cursor[1]>=0 and cursor[1]<31)))):
					scan_FOV.append(cursor)
					
					#print(scan_FOV)
					
			if (len(scan_FOV)!=0):
				
				np_scan= np.array(scan_FOV)
				
				while(len(scan_FOV)<n_clusters):
					n_clusters= n_clusters-1
					
				scan_kmeans=KMeans(n_clusters)
				kmeans_scan_obj=scan_kmeans.fit(np_scan)
				min_scan=kmeans_scan_obj.cluster_centers_
				
				#print("Clustered Scan: ",min_scan)
				socket.send(pickle.dumps(min_scan))

				#  Get the reply.
				message = socket.recv()
				#print("Received reply: %s"%message)
			
			
			
			
		break;
	
	except KeyboardInterrupt:
		print("\nLidar Interrupt Accepted")
		break;
	except:
		pass




		
		
		
    
    #print(scan)
    #if i > 1000:
       # break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
print("Lidar Stopped")
