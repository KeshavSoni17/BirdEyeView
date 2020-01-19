#!/usr/bin/env python

from flask import Flask, render_template, Response #imports
import cv2
import sys
import numpy as np
import math
from PIL import Image
import os
import re

app = Flask(__name__)#app


@app.route('/')
def index():
    return render_template('index.html')#renders using html page


def getNum(path):
    if path.endswith("0"):
        return 0
    elif path.endswith("1"):
        return 1
    elif path.endswith("2"):
        return 2
    return 3



def deleteblack(src):

    #lower = np.array([0,0,0])
    #higher = np.array([0,0,0])
    #mask = cv2.inRange(img, lower, higher)
    #res = cv2.bitwise_and(img, img, mask= mask)
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(src)
    rgba = [b,g,r, alpha]
    dst = cv2.merge(rgba,4)
    return dst

def transformation(cap, imgHeight, imgWidth, theta, screenh, screenw):
    _, frame = cap.read()
    north = frame
    south = frame
    east = frame
    west = frame

    result = np.zeros((screenh, screenw, 3), np.uint8)

    # North - check if right
    north = cv2.resize(north, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    north = cv2.warpPerspective(north, matrix, (imgWidth, imgHeight))

    # South
    south = cv2.resize(south, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    south = cv2.warpPerspective(south, matrix, (imgWidth, imgHeight))

    # East
    east = cv2.resize(east, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    east = cv2.warpPerspective(east, matrix, (imgWidth, imgHeight))

    # West
    west = cv2.resize(west, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    west = cv2.warpPerspective(west, matrix, (imgWidth, imgHeight))

    north = cv2.resize(north, (int(screenw / 3), int(screenh / 3)))
    x_offset = imgHeight-int(imgWidth/3)
    y_offset = 0
    result[y_offset:y_offset + len(north), x_offset:x_offset + len(north[1])] = north


    south = cv2.resize(south, (int(screenw / 3), int(screenh / 3)))
    south = np.rot90(south)
    south = np.rot90(south)
    x_offset = imgHeight-int(imgWidth/3)
    y_offset = imgHeight+int(imgWidth/3)
    result[y_offset:y_offset + len(south), x_offset:x_offset + len(south[1])] = south

    west = cv2.resize(west, (int(screenw / 3), int(screenh / 3)))
    west = np.rot90(west)
    west = np.rot90(west)
    west = np.rot90(west)
    x_offset = imgHeight+int(imgWidth/3)
    y_offset = imgHeight-int(imgWidth/3)
    #west = deleteblack(west)
    result[y_offset:y_offset + len(west), x_offset:x_offset + len(west[1])] += west

    east = cv2.resize(east, (int(screenw / 3), int(screenh / 3)))
    east = np.rot90(east)
    x_offset = int(0)
    y_offset = int(screenh / 3)-int(imgWidth/3)
    result[y_offset:y_offset + len(east), x_offset:x_offset + len(east[1])] += east
    #    east = cv2.resize(east, (int(screenw/3), int(screenh/3)))
    #    east = np.rot90(east)
    #    east = np.rot90(east)
    #    x_offset = 0 + int(len(east[1]))
    #    y_offset = int(screenh/3)-int(len(east)*1/4)
    #    result[y_offset:y_offset+len(east), x_offset:x_offset+len(east[1])] = east

    # frame = cv2.resize(frame, (640,360), interpolation = cv2.INTER_AREA)
    #
    result = result[0:imgHeight+int(imgWidth/3)+imgHeight, 0:imgHeight+int(imgWidth/3)+imgHeight]

    return result


def get_frame():
    # camera_port=1 #for sep camera
    camera_port = 1#getNum(os.readlink("/dev/ARC_International_CAM"))  # getNum(os.readlink("/dev/LOGITECH_C310_TOP"))
    print(camera_port)
    cap = cv2.VideoCapture(camera_port)  # this makes a web cam object

    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 720)

    #screenh/screenw should be = imgHeight/imgWidth for best results
    screenh = 120*3
    screenw = 160*3

    imgHeight = int(screenh/3)
    imgWidth = int(screenw/3)

    theta = 45 * math.pi / 180
    height = 2

    while True:
        imgencode = cv2.imencode('.jpg', transformation(cap, imgHeight, imgWidth, theta, screenh, screenw))[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')

    del (camera)


@app.route('/calc')
def calc():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='10.8.46.134', debug=True, threaded=True)
