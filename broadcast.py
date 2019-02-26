import zmq
import _thread
from threading import Lock

context = zmq.Context()
mutex = Lock()

#  Socket to talk to server
print("Connecting to fusion engine")
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5560")

def comms_thread():
	while True:
		message = socket.recv_string()
		socket.send(b"world")
        mutex.acquire()

        #compute GPS coordinates of all the detected pedestrians
        #set new detections flag

		mutex.release()

def GPS_thread():
    while True:
        print("Query GPS")

try: 
	_thread.start_new_thread(comms_thread, ())
    _thread.start_new_thread(GPS_thread, ())
except:
	print("Error: Unable to start thread")

while(True):
    mutex.acquire()

    #broadcast computed pedestrian data


    mutex.release()
