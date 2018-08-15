import cv2
import numpy as np
import time

#camera runs at 100 frames in 17 seconds
#from 112 website
def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

def alternateChangeDirection(pointsList):
    if len(pointsList)<5:
        return False
    if pointsList[-3][0] ==None or pointsList[-2][0] ==None or pointsList[-1][0] == None:
        return False
    dx1 = pointsList[-3][0] - pointsList[-2][0]
    dx2 = pointsList[-2][0] - pointsList[-1][0]
    if abs(dx1-dx2) <50:
        return False
    if dx1 <0 and dx2>0:
        return True
    elif dx1 >0 and dx2 <0:
        return True
    return False

def vidRoll(color):

    #needed to calculate and test out different values for bgr, such that they 
    #match the different colors. 
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])
    lower_red = np.array([25,25,150])
    upper_red = np.array([50,56,255])
    lower_green=np.array([33,80,40])
    upper_green=np.array([102,255,255])
    lower_yellow = np.array([20,100,100])
    upper_yellow = np.array([30, 255, 255])

    startFrame = 50 
    pointsList = []
    dframes = 0
    bpm = 0
    cap = cv2.VideoCapture(0)
    startTime = time.time()
    frameNumber =0 #starts drawing when it hits this number
    changedList = []
   # while time.time()-startTime<30:
    #while True:
    rollIt = True
    cv2.startWindowThread()
    while True:
        # Take each frame
        _, frame = cap.read()
        frameNumber+=1 #increments frame number in order to keep track of time

        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)

        # Threshold the HSV image to get only blue colors
        if color == 'blue':
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
        if color == 'yellow':
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        if color == 'red':
            mask = cv2.inRange(hsv, lower_red, upper_red)
        if color == 'green':
            mask = cv2.inRange(hsv, lower_green, upper_green)
        #remove background noise
        mask = cv2.erode(mask, None, iterations = 6) #get rid of all blosb
        mask = cv2.dilate(mask, None, iterations = 6) #increase the size back up to original 

        #find contours can only operate on 
        currContour = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        #second to last part of find contours 
        center = None

        if len(currContour) > 0:
            c = max(currContour, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            if radius > 30: 
                center = (int(x), int(y))
                cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
                thickness = int(radius//4)

        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask= mask)
        if center != None:
            if frameNumber >startFrame and len(pointsList)==0:
                pointsList.append(center)
            elif len(pointsList)>0:
                diffX = abs(pointsList[-1][0] - center[0])
                diffY = abs(pointsList[-1][1] - center[1])
                if (5<diffX<400 and 5<diffY<400):
                    pointsList.append(center)
                
                
        for i in range (len(pointsList)-1):
            cv2.line(frame, pointsList[i], pointsList[i+1], (255, 0, 0), 2)

        if len(pointsList)>50: 
            pointsList = pointsList[1:]

        directionChange = 0
        try:
            if alternateChangeDirection(pointsList):
                #print("changed direction%s"%(directionChange))
                directionChange +=1
                changedList.append(time.time()-startTime)
        except:
            pass
        if len(changedList)>0 and frameNumber%20 == 0:
            bpm = calculatePace(changedList)

        if (len(changedList)>100):
            changedList = changedList[1:]
        if frameNumber<= startFrame:
            cv2.putText(frame, "Wait to start running", (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
            cv2.putText(frame, "Get ready by placing colored object in frame", (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))


        # if frameNumber >startFrame and bpm == 0:
        #     cv2.putText(frame, "Start Running!", (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
        #     counter = time.time()-startTime
        #     cv2.putText(frame, "countdown: %.2f"%counter, (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
            

        if bpm != 0:
            cv2.putText(frame,"Current Beats per Minute: %s"%(bpm),  (0, 100), cv2.FONT_HERSHEY_PLAIN, 2, (238,130, 238))
        cv2.imshow('frame',frame)
        # cv2.imshow('mask',mask)
        # cv2.imshow('res',res)
        waitTime = 5    
        if cv2.waitKey(waitTime) & 0xFF == ord('q'):
            break
    print('quit')
    cap.release()
    cv2.destroyAllWindows()
    return bpm

def calculatePace(timeStampList):
    dt =0 
    pace =0
    for i in range(len(timeStampList)-1):
        dt += (timeStampList[i+1] - timeStampList[i])
    dt /= len(timeStampList)
    if dt !=0:
        pace = 60/dt
    return int(pace)

#vidRoll()