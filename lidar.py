'''
lidar.py

Lidar process: Runs the LIDAR sensor and communicates with the fusion.py process.

'''

from rplidar import RPLidar
import zmq
import _pickle as pickle
import numpy as np  
from sklearn.cluster import KMeans 
import time
import mkmath as mk

def mkmeans(scan):
    
    length=len(scan)
    i=0
    running_r=[]
    running_theta=[]
    running_quality=42
    final=[]
    got_new=False
    try:
        for cursor in scan:
                
            if(i==(length-1)):
                    running_r.append(scan[i][1])
                    running_theta.append(scan[i][2])
                    temp=[]
                    temp.append(15)
                    temp.append( sum(running_r)/len(running_r))
                    temp.append( sum(running_theta)/len(running_theta))
                    final.append(temp)
                    running_r.clear()
                    running_theta.clear()
                    break
                       
            elif( (abs(cursor[1]-scan[i+1][1])<2)):
                    
                    running_r.append(cursor[1])
                    running_theta.append(cursor[2])
            elif(abs(cursor[1]-scan[i+1][1])>2):
                    running_r.append(scan[i][1])
                    running_theta.append(scan[i][2])
                    got_new=True
                    temp=[]
                    temp.append(15)
                    temp.append( sum(running_r)/len(running_r))
                    temp.append( sum(running_theta)/len(running_theta))
                    final.append(temp)
                    running_r.clear()
                    running_theta.clear()
            i=i+1
                        
    except:
        print("Stupid",i)

    return final
			
#socket
context = zmq.Context()
print("Lidar Process: Connecting to Fusion Engine…")
socket = context.socket(zmq.REQ)
print("Connection Status:",socket.connect("tcp://localhost:5556"))

#lidar initialization
lidar = RPLidar('/dev/ttyUSB0')

lidar.clear_input()

enable_kmeans=False

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
		
		time.sleep(0)
		
		for i, scan in enumerate(scan_gen):
			scan_FOV.clear()
			n_clusters=10
			
			for cursor in scan:
				if((cursor[2]<8000) and((cursor[1]>300 and cursor[1]<361)or((cursor[1]>=0 and cursor[1]<60)))):
					scan_FOV.append(cursor)
					
			if (len(scan_FOV)!=0):
				
				if(enable_kmeans):
					
					np_scan= np.array(scan_FOV)
					
					while(len(scan_FOV)<n_clusters):
						n_clusters= n_clusters-1
						
					scan_kmeans=KMeans(n_clusters)
					kmeans_scan_obj=scan_kmeans.fit(np_scan)
					min_scan=kmeans_scan_obj.cluster_centers_
					socket.send(pickle.dumps(min_scan))
				else:
					final_scan=mk.mkmeans2(scan_FOV)
					socket.send(pickle.dumps(scan_FOV))

				#  Get the reply.
				message = socket.recv()	
		break
	
	except KeyboardInterrupt:
		print("\nLidar Interrupt Accepted")
		break
	except:
		pass

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
print("Lidar Stopped")