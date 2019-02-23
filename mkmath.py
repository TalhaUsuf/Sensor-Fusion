#Math Repository For Useful Functions

#imports
import math
import numpy as np

#functions
def convertToCartesian(radius,angle):
    #expecting angle in degrees
    cartesian= {"x": 0, "y":0}
    x_cord= radius*math.cos(math.pi/180*angle)
    y_cord= radius*math.sin(math.pi/180*angle)
    cartesian["x"]=x_cord
    cartesian["y"]=y_cord
    return cartesian

#print(convertToCartesian(5,53))

def convertToCartesanRadians(radius,radians):
    #expecting angle in radians
    #gets converted to degrees
    angle= radians *180/math.pi
    cartesian= {"x": 0, "y":0}
    x_cord= radius*math.cos(angle)
    y_cord= radius*math.sin(angle)
    cartesian["x"]=x_cord
    cartesian["y"]=y_cord
    #print(cartesian)
    return cartesian    
    


  
"""Lidar/Radar""" 

def convertWithoutRT(U,fx,fy,cx,cy,Sx,Sy):
   
	UVW= np.array(U)
	intrinsic= np.array([[fx/Sx,0,cx],[0,fy/Sy,cy],[0,0,1]])
	m= intrinsic.dot(UVW)
	if(m[2]==0):
		m[2]=1
		
	m[0]=m[0]/m[2]
	m[1]=m[1]/m[2]
	m[2]=1
    #print("PIXELS=",m)
	return m

def convertToCamCoords(U,V,W,RT):
    #print("\n convert To CAM\n")
    UVW= np.array([[U],[V],[W],[1]])
    #print("\nXTZ",UVW)
    #print("RT",RT)
    return RT.dot(UVW)

def LidToPixels(X,Y,Z,RT,fx,fy,Sx,Sy,Cx,Cy):
    cam_cords=convertToCamCoords(X,Y,Z,RT)
    pixels=convertWithoutRT(cam_cords,fx,fy,Cx,Cy,Sx,Sy)
    return [int(pixels[0]), int(pixels[1]), int(pixels[2])]


    
"""
RT=np.matrix('1 0 0 0;0 1 0 0;0 0 1 0.01;0 0 0 1')
m = convertWorldCordsToPixels(1.5,10,0.5,715,98,98,RT,4,3)
print(m)
"""
