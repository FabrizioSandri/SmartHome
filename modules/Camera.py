from threading import Thread, Lock
import cv2
import time

class Camera:

  def __init__(self, url, numCameras):
    self.cap = cv2.VideoCapture(url)
    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    self.numCameras = numCameras
    self.exit_flag = time.time()
    self.lock = Lock()

    t = Thread(target=self.passiveRead)
    t.daemon = True
    t.start()
  
  # read frames as soon as they are available, keeping only most recent one
  def passiveRead(self):
    while True:
        if time.time() - self.exit_flag > 3: # after 3 seconds of inactivity stop the stream
            self.cap.release()
            break
        self.lock.acquire()
        self.cap.grab()
        self.lock.release()
        time.sleep(0.05)

  def getFrame(self):
    self.lock.acquire()
    ret, frame = self.cap.read()
    self.lock.release()
    self.exit_flag = time.time()

    # if more than one camera, resize the image
    if int(self.numCameras) > 1:
        frame = cv2.resize(frame,None,fx=0.5,fy=0.5) 

    ret, frame = cv2.imencode('.jpg', frame)
    return frame
