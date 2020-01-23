from imutils.video import WebcamVideoStream
from flask import Flask, render_template, Response #imports
import cv2
import sys
import numpy as np
import math
from PIL import Image
import os
import re
import time

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

def transformation(cap, imgHeight, imgWidth, theta, screenh, screenw):
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

# West (left)
    west = cv2.resize(west, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    west = cv2.warpPerspective(west, matrix, (imgWidth, imgHeight))

# East (right)
    east = cv2.resize(east, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)
    pts1 = np.float32([(0, imgHeight), (imgWidth, imgHeight), (imgWidth, 0), (0, 0)])
    pts2 = np.float32(
        [(imgWidth / 2 - imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth / 2 + imgWidth / 2 * math.cos(theta + math.pi / 6) / math.cos(theta - math.pi / 6), imgHeight),
         (imgWidth, 0), (0, 0)])
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
   # north = cv2.VideoCapture(0)
   # north = cv2.VideoCapture(0).start()
   # north_port = getNum(os.readlink("/dev/LOGITECH_C310_BOT"))
    north = WebcamVideoStream(src=0).start()
   # south_port = getNum(os.readlink("/dev/ARC_International_CAM"))
    south = WebcamVideoStream(src=1).start()
   # east_port = getNum(os.readlink("/dev/LOGITECH_C310_RIGHT"))
    east = WebcamVideoStream(src=2).start()
   # west_port = getNum(os.readlink("/dev/LOGITECH_C310_LEFT")) 
   # west = WebcamVideoStream(src=1).start()
#    north.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
#    north.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
#    north.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,120)
#    north.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 160)
    cap = [north,south,north,east]
#    time.sleep(1000000000)
    screenh = 240*3
    screenw = 320*3

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
    app.run(host='10.8.46.176', debug=True, threaded=True)
