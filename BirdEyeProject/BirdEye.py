from flask import Flask, render_template, request, Response, redirect
import cv2
import sys
import numpy as np
import math
from PIL import Image
import os
import re
import time
import threading
from threading import Thread
import pickle

class WebcamVideoStream:
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            
    def read(self):
        return self.frame
    
    def stop(self):
        self.stopped = True
        
def calibration(img, imgWidth, imgHeight):
	img = cv2.resize(img,(imgWidth,imgHeight))
	grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blurr = cv2.GaussianBlur(grey, (5,5),0)
	edge = cv2.Canny(blurr, 0, 50)
	contours, _ = cv2.findContours(edge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea, reverse= True)
	for i in contours:
		elip =  cv2.arcLength(i, True)
		approx = cv2.approxPolyDP(i,0.08*elip, True)
		if len(approx) == 4 :
			doc = approx
			break
	cv2.drawContours(img, [doc], -1, (0, 255, 0), 2)
	doc=doc.reshape((4,2))
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

#Decleration of Variables
northPort = 0
southPort = 0
north = WebcamVideoStream(src=northPort).start()
south = WebcamVideoStream(src=southPort).start()

northFile = "/Users/sonifamily/Documents/BirdEyeProject/north_transformation.npy"
southFile = "/Users/sonifamily/Documents/BirdEyeProject/south_transformation.npy"
portFile = "/Users/sonifamily/Documents/BirdEyeProject/port.npy"
np.save(portFile,[0,0])
cap = [north,south]

imgWidth = 160
imgHeight = 120

screenw = imgWidth*3
screenh = imgHeight*3

northTransformation = None
southTransformation = None
transformationArray = None

if(len(np.load(northFile))==0):
    northImage = cap[0].read()
    northImage = cv2.resize(northImage, (imgWidth, imgHeight),interpolation=cv2.INTER_AREA)
    northTransformation = calibration(northImage,len(northImage[0]),len(northImage))
    np.save(northFile,northTransformation)
else:
    northTransformation = np.load(northFile)
    
if(len(np.load(southFile))==0):
    southImage = cap[1].read()
    southImage = cv2.resize(southImage, (imgWidth, imgHeight),interpolation=cv2.INTER_AREA)
    southTransformation = calibration(southImage,len(southImage[0]),len(southImage))
    np.save(southFile,southTransformation)
else:
    southTransformation = np.load(southFile)


def recalibrate_north():
    northImage = cap[0].read()
    northImage = cv2.resize(northImage, (imgWidth, imgHeight),interpolation=cv2.INTER_AREA)
    northTransformation = calibration(northImage,len(northImage[0]),len(northImage))
    np.save(northFile,northTransformation)
    
def recalibrate_south():
    southImage = cap[1].read()
    southImage = cv2.resize(southImage, (imgWidth, imgHeight),interpolation=cv2.INTER_AREA)
    southTransformation = calibration(southImage,len(southImage[0]),len(southImage))
    np.save(southFile,southTransformation)

app = Flask(__name__)
    
def transformation(cap,array):
    north = cap[0].read()
    south = cap[1].read()

    result = np.zeros((screenh, screenw, 3), np.uint8)
    
    north = cv2.resize(north, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = array[0][0]
    pts2 = array[0][1]
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    north = cv2.warpPerspective(north, matrix, (imgWidth, imgHeight))

    south = cv2.resize(south, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = array[1][0]
    pts2 = array[1][1]
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    south = cv2.warpPerspective(south, matrix, (imgWidth, imgHeight))

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

    result = result[0:imgHeight+int(imgWidth/3)+imgHeight, 0:imgHeight+int(imgWidth/3)+imgHeight]
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    return result

def get_frame():
    a = int(np.load(portFile)[0])
    b = int(np.load(portFile)[1])
    north = WebcamVideoStream(src=a).start()
    south = WebcamVideoStream(src=b).start()
    cap = [north,south]
    northTransformation = np.load(northFile)
    southTransformation = np.load(southFile)
    transformationArray = [northTransformation,southTransformation]
    while True:
        imgencode = cv2.imencode('.jpg', transformation(cap, transformationArray))[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')


@app.route('/')
def calc():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/calibrateCameras',methods = ['POST'])
def settingPage():
    if request.form['button']=="North Calibrate":
        northTransformation = recalibrate_north()
    elif request.form['button']=="South Calibrate":
        southTransformation = recalibrate_south()
    elif request.form['button']=="Submit":
        a = request.form['northPort']
        b = request.form['southPort']
        np.save(portFile,[a,b])
    calc()
    return redirect("http://0.0.0.0:5802/setting")

@app.route('/setting')
def setting():
    return render_template('setting.html')

if __name__ == '__main__':
   app.run('0.0.0.0',debug = True,port = 5802)
