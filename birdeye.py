#from imutils.video import WebcamVideoStream
from flask import Flask, render_template, Response #imports
#import WebcamVideoStream
import cv2
import sys
import numpy as np
import math
from PIL import Image
import os
import re
import time
from threading import Thread

class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
    	(self.grabbed, self.frame) = self.stream.read()
    	self.stream.set(3,320)
    	self.stream.set(4,240)
    	self.stream.set(15,-8.0)
    	self.stream.set(5, 10)
    	# initialize the variable used to indicate if the thread should
    	# be stopped
    	self.stopped = False
    def start(self):
        # start the thread to read frames from the video stream
	Thread(target=self.update, args=()).start()
        return self
 
    def update(self):
        # keep looping infinitely until the thread is stopped
    	while True:
            # if the thread indicator variable is set, stop the thread
		if self.stopped:
                    return
 
	    	# otherwise, read the next frame from the stream
    		(self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# return the frame most recently read
	    return self.frame
 
    def stop(self):
        # indicate that the thread should be stopped
    	self.stopped = True

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def getNum(path):
    if path.endswith("0"):
        return 0
    elif path.endswith("1"):
        return 1
    elif path.endswith("2"):
        return 2
    return 3

def calibration(img, imgWidth, imgHeight):
	#function inputs img, imgWidth,imgHeight,
	img = cv2.resize(img,(imgWidth,imgHeight))
#convert image to grayscale
	grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#blurr image to smooth
	blurr = cv2.GaussianBlur(grey, (5,5),0)
#finding edges
	edge = cv2.Canny(blurr, 0, 50)
#apadtive threshold and canny gave similar final output
#threshold = cv2.adaptiveThreshold(blurr ,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
#find contours in thresholded image and sort them according to decreasing area
	contours, _ = cv2.findContours(edge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea, reverse= True)
#contour approximation
	for i in contours:
		elip =  cv2.arcLength(i, True)
		approx = cv2.approxPolyDP(i,0.08*elip, True)
		if len(approx) == 4 :
			doc = approx
			break
#draw contours
	cv2.drawContours(img, [doc], -1, (0, 255, 0), 2)
#reshape to avoid errors ahead
	doc=doc.reshape((4,2))
#create a new array and initialize
	new_doc = np.zeros((4,2), dtype="float32")
	Sum = doc.sum(axis = 1)
	new_doc[0] = doc[np.argmin(Sum)]
	new_doc[2] = doc[np.argmax(Sum)]
	Diff = np.diff(doc, axis=1)
	new_doc[1] = doc[np.argmin(Diff)]
	new_doc[3] = doc[np.argmax(Diff)]
	(tl,tr,br,bl) = new_doc
	dst = np.array([[tl[0],tr[1]],[tr[0], tr[1]],[tr[0], bl[1]], [tl[0], bl[1]]], dtype="float32")
	return(new_doc, dst)

def transformation(cap, imgHeight, imgWidth,screenh, screenw,array):
    north = cap[0].read()
    south = cap[1].read()
    west = cap[2].read()
    east = cap[3].read()
   # south = north
   # west = north
   # east = north
    result = np.zeros((screenh, screenw, 3), np.uint8)
# North - check if right
    north = cv2.resize(north, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = array[0]
    pts2 = array[1]
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    north = cv2.warpPerspective(north, matrix, (imgWidth, imgHeight))

# South
    south = cv2.resize(south, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    south = cv2.warpPerspective(south, matrix, (imgWidth, imgHeight))

# West (left)
    west = cv2.resize(west, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    west = cv2.warpPerspective(west, matrix, (imgWidth, imgHeight))

# East (right)
    east = cv2.resize(east, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    east = cv2.warpPerspective(east, matrix, (imgWidth, imgHeight))
    square_offset = 0
    north = cv2.resize(north, (int(screenw / 3), int(screenh / 3)))
    x_offset = imgHeight-int(imgWidth/3)
    y_offset = square_offset
    result[y_offset:y_offset + len(north), x_offset:x_offset + len(north[1])] += north


    south = cv2.resize(south, (int(screenw / 3), int(screenh / 3)))
    south = np.rot90(south)
    south = np.rot90(south)
    x_offset = imgHeight-int(imgWidth/3)
    y_offset = imgHeight+int(imgWidth/3)-square_offset
    result[y_offset:y_offset + len(south), x_offset:x_offset + len(south[1])] += south

    east = cv2.resize(east, (int(screenw / 3), int(screenh / 3)))
    east = np.rot90(east)
    east = np.rot90(east)
    east = np.rot90(east)
    x_offset = imgHeight+int(imgWidth/3)-square_offset
    y_offset = imgHeight-int(imgWidth/3)
    result[y_offset:y_offset + len(east), x_offset:x_offset + len(east[1])] += east

    west = cv2.resize(west, (int(screenw / 3), int(screenh / 3)))
    west = np.rot90(west)
    x_offset = int(0)+square_offset
    y_offset = int(screenh / 3)-int(imgWidth/3)
    result[y_offset:y_offset + len(west), x_offset:x_offset + len(west[1])] += west

    result = result[0:imgHeight+int(imgWidth/3)+imgHeight, 0:imgHeight+int(imgWidth/3)+imgHeight]

    return result

def get_frame():
    north = WebcamVideoStream(src=2).start()
    
    cap = [north,north,north,north]
    screenh = 240*3
    screenw = 320*3

    imgHeight = int(screenh/3)
    imgWidth = int(screenw/3)

    theta = 45 * math.pi / 180
    height = 2
    
    frame = north.read()
    frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=10)
    cv2.imwrite("frame.jpg",frame)
    frame = cv2.resize(frame, (imgWidth, imgHeight),interpolation=cv2.INTER_AREA)
    array = calibration(frame,len(frame[0]),len(frame))
    print(array)
    while True:
        imgencode = cv2.imencode('.jpg', transformation(cap, imgHeight, imgWidth, screenh, screenw,array))[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')

    del (camera)


@app.route('/calc')
def calc():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)





