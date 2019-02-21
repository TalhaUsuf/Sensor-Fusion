#imports
from rplidar import RPLidar
import zmq
import _pickle as pickle

#socket
context = zmq.Context()
print("Lidar Executable: Connecting to Fusion Engine…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")

#lidar initialization
lidar = RPLidar('/dev/ttyUSB0')

#diagnostics
info = lidar.get_info()
print(info)
health = lidar.get_health()
print(health)



for i, scan in enumerate(lidar.iter_scans()):
    print('%d: Got %d measurments' % (i, len(scan)))
    print("Sending Scan")
    socket.send(pickle.dumps(scan))

    #  Get the reply.
    message = socket.recv()
    print("Received reply: %s"%message)
    
    #print(scan)
    #if i > 1000:
       # break

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
