#Math Repository For Useful Functions

#imports
import math
import numpy as np

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
				
			#print(i)

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
					break;
					   
			elif( (abs(cursor[1]-scan[i+1][1])<2)):
					
					running_r.append(cursor[1])
					#print("running R",running_r)
					running_theta.append(cursor[2])
					#print("running theta",running_theta)
			elif(abs(cursor[1]-scan[i+1][1])>2):
					running_r.append(scan[i][1])
					running_theta.append(scan[i][2])
					#print("LARGER")
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

def mkmeans2(scan):
	length=len(scan)
	i=0
	running_r=[]
	temp=[]
	running_theta=[]
	running_quality=42
	final=[]
	got_new=False
	res_x=100
	res_y=200
	#print("Scan:",scan)
	
	try:
		for cursor in scan:
				
			#print(i)
			
			cart= convertToCartesian(cursor[2],cursor[1])
			next_cart= cart
			if(i!=length-1):
				next_cart=convertToCartesian(scan[i+1][2],scan[i+1][1])	   
				if( (abs(cart['x']-next_cart['x'])<res_x) and (abs(cart['y']-next_cart['y'])<res_y) ):
						
						#print("Prefinal@", i,final)
						running_r.append(cursor[2])
						running_theta.append(cursor[1])
					
			
							
						
				elif((abs(cart['x']-next_cart['x'])>res_x) or (abs(cart['y']-next_cart['y'])>res_y)):
						running_r.append(cursor[2])
						running_theta.append(cursor[1])
						
						#print("running_r", running_r)
						#print("running_theta",running_theta)
						temp.clear()
						temp.append(15)
						temp.append(average(running_theta))
						temp.append(average(running_r))
						
						#print("temp",temp)
						#rint("Pre Final",final)
						final.append(temp.copy())
						running_r.clear()
						running_theta.clear()
			else:
				running_r.append(cursor[2])
				running_theta.append(cursor[1])
				
				#print("running_r", running_r)
				#print("running_theta",running_theta)
				temp.clear()
				temp.append(15)
				temp.append(average(running_theta))
				temp.append(average(running_r))
				
				#print("temp",temp)
				#rint("Pre Final",final)
				final.append(temp.copy())
				running_r.clear()
				running_theta.clear()
				
						
						#print(i,"-","final",final)
			
				
			
				
				
				
			i=i+1
						
			
	except(e):
		print(e)
		print("Stupid",i)
		
	#print("\nfinal",final)

	return final
	

def average(arr):

	return sum(arr)/len(arr)
  


    
"""
RT=np.matrix('1 0 0 0;0 1 0 0;0 0 1 0.01;0 0 0 1')
m = convertWorldCordsToPixels(1.5,10,0.5,715,98,98,RT,4,3)
print(m)
"""
