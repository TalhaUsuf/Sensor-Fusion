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
                
            print(i)

            if(i==(length-1)):
                    running_r.append(scan[i][1])
                    running_theta.append(scan[i][2])
                    temp=[]
                    temp.append( sum(running_r)/len(running_r))
                    temp.append( sum(running_theta)/len(running_theta))
                    final.append(temp)
                    running_r.clear()
                    running_theta.clear()
                    break;
                       
            elif( (abs(cursor[1]-scan[i+1][1])<20)):
                    
                    running_r.append(cursor[1])
                    #print("running R",running_r)
                    running_theta.append(cursor[2])
                    #print("running theta",running_theta)
            elif(abs(cursor[1]-scan[i+1][1])>250):
                    running_r.append(scan[i][1])
                    running_theta.append(scan[i][2])
                    #print("LARGER")
                    got_new=True
                    temp=[]
                    temp.append( sum(running_r)/len(running_r))
                    temp.append( sum(running_theta)/len(running_theta))
                    final.append(temp)
                    running_r.clear()
                    running_theta.clear()
            i=i+1
                        
            
    except:
        print("Stupid",i)

    return final


scan= [[13,20,100],[13,21,101],[13,25,102],[13,400,200],[13,400,200],[13,400,250]]

print(mkmeans(scan))
