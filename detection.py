from __future__ import division
import imutils
import argparse
import time
import datetime
import cv2
import accelerometer
from pyaudio import PyAudio
from detector import Detector
from SoundDriver import SoundDriver


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", default=False,action="store_true",
	help="whether or not the Raspberry Pi camera should be used")

ap.add_argument("-d", "--display", default=False,action="store_true",
    help="whether or not to display the image")

ap.add_argument("-a", "--analytics", default=False,action="store_true",
    help="whether or not analytics will be tracked")

ap.add_argument("-b", "--debug", default=False,action="store_true",
    help="whether or not debugger is active")

ap.add_argument("-s", "--sound", default=False,action="store_true",
    help="whether or not sound is active")

ap.add_argument("-c", "--accelerometer", default=False,action="store_true",
    help="whether or not accelerometer code is running")

args = vars(ap.parse_args())

if args["sound"]:
    SoundDriver = SoundDriver()

detector = Detector()
frameRate = 0
initial_time = datetime.datetime.now()
start_time = time.time()
MOVING = True

VideoStream = None
if args['picamera']:
    from PiCameraVideoStream import PiCameraVideoStream
    VideoStream = PiCameraVideoStream()
else:
    isRaspberryPi = 0
    from WebCamVideoStream import WebCamVideoStream
    VideoStream = WebCamVideoStream()


while True:
    curr_time = time.time()
    threshold = 5 if MOVING else 3

    frame_time = (datetime.datetime.now() - initial_time).total_seconds()
    if args["analytics"]:
        print(1/frame_time)

    initial_time = datetime.datetime.now()


    if args["accelerometer"]:
        if((curr_time - start_time) // threshold > 1):
            accel_data = accelerometer.run()
            if accel_data > 13:
                MOVING = True
            else:
                MOVING = False

    frame = VideoStream.getFrame()
    frameRate+=1

    frame = imutils.resize(frame, width=450)

    if MOVING or not args["accelerometer"]: 
        distracted= detector.isDistracted(frame,args["display"])
        if distracted:
            if args["sound"]:
                SoundDriver.play_sound()
            if args["display"]:
                detector.display_warnings(frame)

    if (args["display"] and MOVING):
        detector.display_moving(frame)
    if (args["display"]):
        detector.show(frame)

    VideoStream.reset()

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
    	break

SoundDriver.stream.stop_stream()
VideoStream.close()
cv2.destroyAllWindows()
