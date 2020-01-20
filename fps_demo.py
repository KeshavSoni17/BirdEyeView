from flask import Flask, render_template, Response
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import math
import re
import numpy as np
import threading

imgHeight = 160
imgWidth = 160
screenh = imgHeight*4
screenw = imgHeight*4
theta = 45 * math.pi / 180
height = 2
output = [0,0,0,0]
result = np.zeros((screenh, screenw, 3), np.uint8)

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

def thread_process(vs,num,theta,imgWidth,imgHeight,screenh,screenw):
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
 
def get_frame():
    vs = WebcamVideoStream(src=0).start()
    
    while True:
        imgencode = cv2.imencode('.jpg', transformation(vs, imgHeight, imgWidth, theta, screenh, screenw))[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')



@app.route('/calc')
def calc():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='localhost', debug=True, threaded=True)
