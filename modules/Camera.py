from threading import Thread, Lock
import cv2 as cv
import time

class Camera :
    
    def __init__(self, url, numCameras):
        self.camera = cv.VideoCapture(url)
        self.mutex_M = Lock()
        self.mutex_N = Lock()
        self.exit_flag = time.time()
        self.numCameras = numCameras

        self.t = Thread(target=self.passiveRead)
        self.t.daemon = True
        self.t.start()

    def passiveRead(self):
        while True:

            if time.time() - self.exit_flag > 3: # after 3 seconds of inactivity stop the stream
                self.camera.release()
                break

            self.mutex_N.acquire() 
            self.mutex_M.acquire() 
            self.mutex_N.release()

            self.camera.grab()

            self.mutex_M.release()

    def getFrame(self):
        self.exit_flag = time.time()
        
        self.mutex_N.acquire() 
        self.mutex_M.acquire() 
        self.mutex_N.release()

        success,frame = self.camera.read()
        self.mutex_M.release()

        # if more than one camera, resize the image
        if int(self.numCameras) > 1:
            frame = cv.resize(frame,None,fx=0.5,fy=0.5) 
        
        ret, frame = cv.imencode('.jpg', frame)

        return success,frame
