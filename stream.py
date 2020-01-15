#!/usr/bin/env python
from flask import Flask, render_template, Response
import cv2
import sys
import numpy as np
import math
from PIL import Image
import os
import re

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

def crop_image_only_outside(img):
    # img is 2D image data
    # tol  is tolerance
    height, width = img.shape[0:2]
    startRow = int(height*.15)
    startCol = int(width*.25)
    endRow = int(height*.85)
    endCol = int(width*.75)
    return img[startRow:endRow, startCol:endCol]

def transformation(cap, imgHeight,imgWidth, theta, screenh,screenw):
    _, frame = cap.read()
    north = frame
    south = frame
    east = frame
    west = frame

    result = np.zeros((screenh,screenw,3),np.uint8)
    # #cv2.imshow("Image",frame)
    #
    #North - check if right
    north = cv2.resize(north, (imgWidth,imgHeight), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(imgWidth/2-imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth/2+imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    north = cv2.warpPerspective(north, matrix, (imgWidth, imgHeight))

    #South
    south = cv2.resize(south, (imgWidth,imgHeight), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(imgWidth/2-imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth/2+imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    south = cv2.warpPerspective(south, matrix, (imgWidth, imgHeight))

    #East
    east = cv2.resize(east, (imgWidth,imgHeight), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(imgWidth/2-imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth/2+imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    east = cv2.warpPerspective(east, matrix, (imgWidth, imgHeight))


    #West
    west = cv2.resize(west, (imgWidth,imgHeight), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(imgWidth/2-imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth/2+imgWidth/2*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    west = cv2.warpPerspective(west, matrix, (imgWidth, imgHeight))

    north = cv2.resize(north, (int(screenw/3), int(screenh/3)))
    x_offset=int(screenw/3)
    y_offset=0
    result[y_offset:y_offset+len(north), x_offset:x_offset+len(north[1])] = north

    south = cv2.resize(south, (int(screenw/3), int(screenh/3)))
    south = cv2.rotate(south, cv2.ROTATE_180)
    x_offset = int(screenw/3)
    y_offset = int(screenh/3)*2
    result[y_offset:y_offset+len(south), x_offset:x_offset+len(south[1])] = south

    west = cv2.resize(west, (int(screenw/3), int(screenh/3)))
    west = cv2.rotate(west, cv2.ROTATE_90_CLOCKWISE)
    x_offset = int(screenw/3)*2-int(len(west[1])/4)
    y_offset = int(screenh/3)-int(len(west)/4)
    result[y_offset:y_offset+len(west), x_offset:x_offset+len(west[1])] = west


    east = cv2.resize(east, (int(screenw/3), int(screenh/3)))
    east = cv2.rotate(east, cv2.ROTATE_90_COUNTERCLOCKWISE)
    x_offset = 0 + int(len(east[1]))
    y_offset = int(screenh/3)-int(len(east)*1/4)
    result[y_offset:y_offset+len(east), x_offset:x_offset+len(east[1])] = east

    #frame = cv2.resize(frame, (640,360), interpolation = cv2.INTER_AREA)

    result = crop_image_only_outside(result)
    
    return result

def get_frame():
   # camera_port=1 #for sep camera
    camera_port = 1#getNum(os.readlink("/dev/LOGITECH_C310_TOP"))
    print(camera_port)
    cap=cv2.VideoCapture(camera_port) #this makes a web cam object



    imgHeight = 540
    imgWidth = 960

    screenh = imgHeight
    screenw = imgWidth

    theta = 45*math.pi / 180
    height = 2

    while True:
        imgencode=cv2.imencode('.jpg',transformation(cap,imgHeight,imgWidth,theta,screenh,screenw))[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    del(camera)

@app.route('/calc')
def calc():
     return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    app.run(host='localhost', debug=True, threaded=True)
