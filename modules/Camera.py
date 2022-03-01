from threading import Thread, Lock
import cv2 as cv

class Camera :
    
    def __init__(self, url):
        self.camera = cv.VideoCapture(url)
        self.mutex_M = Lock()
        self.mutex_N = Lock()

        t = Thread(target=self.passiveRead)
        t.daemon = True
        t.start()

    def passiveRead(self):
        while True:
            self.mutex_N.acquire() 
            self.mutex_M.acquire() 
            self.mutex_N.release()

            self.camera.grab()

            self.mutex_M.release()

    def getFrame(self):
        found = False
        frame = None

        self.mutex_N.acquire() 
        self.mutex_M.acquire() 
        self.mutex_N.release()

        success,frame = self.camera.read()
        self.mutex_M.release()

        return success,frame