#imports
import numpy as np
import math
import mkmath as mk
import cv2
import time
import zmq
import _pickle as pickle


#ipc initialization
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

#scaling weight
cw=10000

#start capturing



cap = cv2.VideoCapture(0)


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    message = socket.recv()
    socket.send(b"200")
    payload=pickle.loads(message)

    #print(payload)

    for cursor in payload:
    
        #print(cursor)
        cartesian= mk.convertToCartesian(cursor[2]/1000,cursor[1])
        x= (cartesian["x"])
        y= (cartesian["y"])
       
        """print("X")
        print(x)
        print("Y")
        print(y)"""
       
        RT=np.matrix('0 1 0 0;0 0 1 0.05;1 0 0 -0.06')


        if(cursor[2]<12000 and((cursor[1]>300 and cursor[1]<361)or((cursor[1]>=0 and cursor[1]<61)))):

                     #Revert
            #nagui cam
            #uv =mk.convertLiWorldCoordsCV(x,y,0.75,741,744,315.741,243,RT,4,3)
            #uv=mk.convertWorldCordsToPixelsCV(x,y,0.73,1074,1074,640,361,RT,16,9)

            #mkoldfunction
            #uv=mk.convertWorldCordsToPixelsCV(x,y,0.75,2500,744,320,240,RT,4,3)

            
            uv=mk.LidToPixels(x,y,0,RT,741,741,4/3,1,320,240)
            #print("UV=",uv)

           # print("X=",x,"Y=",y)
            #print("UV===",uv)
            #if( uv[0]<0 or uv[0]>1280 or  uv[1]<0 or uv[1]>720):
            #   print("\nWarning for this guy:\n",uv)

            #SCALING
            distance= cursor[2]/1000
            cw=5
            if(distance>=12):
                cw=5
            elif(distance<0.5):
                cw=100
            else:
                cw= int(100-8.3*distance)
            
            
            #circle=cv2.circle(frame,(uv[0], uv[1]),int(cw/cursor[2]),(0, 191, 255),0)
            circle=cv2.circle(frame,(uv[0], uv[1]),cw,(0, 191, 255),0)

            #circle=cv2.circle(frame,((uv[0]), (uv[1])),5,(0, 191, 255),0)

       

    # Our operations on the frame come here
    circle=cv2.circle(frame,(320,240),100,(255,255,0),0)
    ''' gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)'''

    # Display the resulting frame
    cv2.imshow('frame',circle)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
