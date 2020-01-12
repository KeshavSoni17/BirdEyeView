# USAGE
# python image_stitching.py --images images/scottsdale --output output.png --crop 1

# import the necessary packages
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
from stopwatch import Stopwatch
# construct the argument parser and parse the arguments
stopwatch = Stopwatch()

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", type=str, required=True,
	help="path to input directory of images to stitch")
ap.add_argument("-o", "--output", type=str, required=True,
	help="path to the output image")
ap.add_argument("-c", "--crop", type=int, default=0,
	help="whether to crop out largest rectangular region")
args = vars(ap.parse_args())

# grab the paths to the input images and initialize our images list
print("[INFO] loading images...")
stopwatch.start
imagePaths = sorted(list(paths.list_images(args["images"])))
images = []

# loop over the image paths, load each one, and add them to our
# images to stich list
for imagePath in imagePaths:
	image = cv2.imread(imagePath)
	images.append(image)

# initialize OpenCV's image sticher object and then perform the image
# stitching
stopwatch.stop
print(stopwatch.duration)

print("[INFO] stitching images...")
stopwatch.restart
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
(status, stitched) = stitcher.stitch(images)
cv2.imwrite(args["output"], stitched)
stopwatch.stop
print(stopwatch.duration)
print('done')
# if the status is '0', then OpenCV successfully performed image
# stitching
