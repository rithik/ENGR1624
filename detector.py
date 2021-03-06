import dlib
import cv2
from scipy.spatial import distance
from imutils import face_utils
import time
import datetime
import math
#from SoundDriver import SoundDriver
#SoundDriver = SoundDriver()

FRAMES = 10
t1 = datetime.datetime.now()
delaytime = 3

class Detector():
    def __init__(self, eyesNotVisibleTime=t1, frame_check_time=t1):
        self.eyesNotVisible = 0
        self.flag = 0
        self.tEyesNotVisible = eyesNotVisibleTime
        self.tFrame_check_time = frame_check_time

        (self.lStart,self.lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
        (self.rStart,self.rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

        self.thresh = 0.25
        self.frame_check = 20
        self.detect = dlib.get_frontal_face_detector()
        self.predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def eye_aspect_ratio(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def isDistracted(self, frame, drawing):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = self.detect(gray, 0)
        if len(subjects) == 0:
            self.eyesNotVisible=datetime.datetime.now()
            if (self.eyesNotVisible-self.tEyesNotVisible).seconds >= delaytime: # Distracted checker
                return True
        else:
            self.tEyesNotVisible=datetime.datetime.now()
        print(len(subjects))
        for subject in subjects:
            shape=self.predict(gray,subject)
            shape=face_utils.shape_to_np(shape)#converting to NumPy Array
            leftEye=shape[self.lStart:self.lEnd]
            rightEye=shape[self.rStart:self.rEnd]
            leftEAR=self.eye_aspect_ratio(leftEye)
            rightEAR=self.eye_aspect_ratio(rightEye)
            ear=(leftEAR+rightEAR)/2.0
            leftEyeHull=cv2.convexHull(leftEye)
            rightEyeHull=cv2.convexHull(rightEye)
            if drawing:
                cv2.drawContours(frame,[leftEyeHull],-1,(0,255,0),1)
                cv2.drawContours(frame,[rightEyeHull],-1,(0,255,0),1)
            if ear < self.thresh: # Drowsiness Detector
                self.flag+=1
               	if self.flag>=self.frame_check:
                    return True
            else:
                 self.flag=0
                 return False

    def display_warnings(self, frame):
        cv2.putText(frame, "****************DISTRACTED!****************", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "****************DISTRACTED!****************", (10,325),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    def display_moving(self, frame):
        cv2.putText(frame, "Moving", (10, 80),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    def show(self, frame):
        cv2.imshow("Frame", frame)
