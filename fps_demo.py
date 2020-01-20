# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import math
import re
import numpy as np
import threading

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")

vs = WebcamVideoStream(src=0).start()
fps = FPS().start()
imgHeight = 160
imgWidth = 160
screenh = imgHeight*4
screenw = imgHeight*4
theta = 45 * math.pi / 180
height = 2
output = [0,0,0,0]
result = np.zeros((screenh, screenw, 3), np.uint8)


# loop over some frames...this time using the threaded stream
#############################################################################
#############################################################################
#############################################################################
def thread_process(vs,num,theta,imgWidth,imgHeight,screenh,screenw):
    #print("Starting thread: ", num)
    frame = vs.read()
    frame = cv2.resize(frame, (imgWidth,imgHeight), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(imgWidth/2-imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth/2+imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    frame = cv2.warpPerspective(frame, matrix, (imgWidth, imgHeight))
    frame = cv2.resize(frame, (int(screenw/3), int(screenh/3)))
    if(num==1):
        frame = np.rot90(frame)
        frame = np.rot90(frame)
        x_offset = int(screenw/3)
        y_offset = int(screenh/3)*2 - int(imgHeight/3)
        result[y_offset:y_offset+len(frame), x_offset:x_offset+len(frame[1])] = frame
    elif(num==2):
        frame = np.rot90(frame)
        frame = np.rot90(frame)
        frame = np.rot90(frame)
        x_offset = int(screenw/3)*2 - int(imgWidth/5*2)
        y_offset = int(screenh/3)
        result[y_offset:y_offset+len(frame), x_offset:x_offset+len(frame[1])] = frame
    elif(num==3):
        frame = np.rot90(frame)
        x_offset = 0+int(imgWidth/5*2)
        y_offset = int(screenh/3)
        result[y_offset:y_offset+len(frame), x_offset:x_offset+len(frame[1])] = frame
    else:
        x_offset=int(screenw/3)
        y_offset=int(imgHeight/3)
        result[y_offset:y_offset+len(frame), x_offset:x_offset+len(frame[1])] = frame
    output[num] = frame

def transformation(vs, imgHeight,imgWidth, theta, screenh,screenw):
    threads = []
    for i in range(4):
        #print(i)
        t = threading.Thread(target=thread_process, args=(vs,i,theta,imgWidth,imgHeight,screenh,screenw))
        threads.append(t)
        t.start()
    threads[0].join()
    threads[1].join()
    threads[2].join()
    threads[3].join()

    return result

#############################################################################
#############################################################################
#############################################################################

while fps._numFrames<500:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
 
	# check to see if the frame should be displayed to our screen
	cv2.imshow("Frame", transformation(vs,imgHeight, imgWidth, theta, screenh, screenw))
	key = cv2.waitKey(1) & 0xFF
 
	# update the FPS counter
	fps.update()
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
