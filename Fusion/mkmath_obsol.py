#Math Repository For Useful Functions

#imports
import math
import numpy as np

#functions
def convertToCartesian(radius,angle):
    #expecting angle in degrees
    cartesian= {"x": 0, "y":0}
    x_cord= radius*math.cos(angle)
    y_cord= radius*math.sin(angle)
    cartesian["x"]=x_cord
    cartesian["y"]=y_cord
    return cartesian

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
    


def computeOpticalCentre(FOV,f):
    #expecting angle in degrees
    return f*math.tan(FOV/2)


"""def convertWorldCordsToPixels(U,V,W,f,FOVx,FOVy,RT,Sx,Sy):
    #expecting RT  to be 4 x 4  numpy matrix
    
    UVW= np.array([[U],[V],[W],[1]]); #real world coords
    per_proj= np.array([[f,0,0,0],[0,f,0,0],[0,0,1,0]]) #pespective projection
    Ox= computeOpticalCentre(FOVx,f)
    Oy= computeOpticalCentre(FOVy,f)
    #Ox=800
    #Oy=600
    Maff= np.array([[1/Sx,0,Ox],[0,1/Sy,Oy],[0,0,1]])

    #incomplete

    print("RT X UVW")
    print(RT.dot(UVW))
    m= Maff.dot(per_proj)
    print("Maff X per_proj")
    print(m)
    m= m.dot(RT)
    print("Maff X per_proj X RT")
    print(m)
    m= m.dot(UVW)
    return m"""

#different math equation than the previous one
def convertWorldCordsToPixels(U,V,W,f,FOVx,FOVy,RT,Sx,Sy):
    #expecting RT  to be 4 x 4  numpy matrix
    
    UVW= np.array([[U],[V],[W],[1]]); #real world coords
    
    #Ox= computeOpticalCentre(FOVx,f)
    #Oy= computeOpticalCentre(FOVy,f)
    Ox=981
    Oy=330
    per_proj= np.array([[f/Sx,0,Ox,0],[0,f/Sy,Oy,0],[0,0,1,0]]) #pespective projection
    

    #incomplete
    #print("RT X UVW")
    m= RT.dot(UVW)
    #print(m)
    m= per_proj.dot(m)
    #print("Per_proj X m")
    #print(m)
    return m


def convertWorldCordsToPixelsCV(U,V,W,fx,fy,cx,cy,RT,Sx,Sy):
    UVW= np.array([[U],[V],[W],[1]]);
    intrinsic= np.array([[fx,0,cx],[0,fy,cy],[0,0,1]])
    identity4Z= np.matrix('1 0 0 0;0 1 0 0;0 0 1 0')
    s= np.array([[1/Sx,0,0],[0,1/Sy,0],[0,0,1]])
    m= RT.dot(UVW)
    #print(m)
    z= intrinsic.dot(identity4Z)
    m= z.dot(m)
    #print(m)
    m=s.dot(m)
    #print(m)
    return m
    
"""
RT=np.matrix('1 0 0 0;0 1 0 0;0 0 1 0.01;0 0 0 1')
m = convertWorldCordsToPixels(1.5,10,0.5,715,98,98,RT,4,3)
print(m)
"""
