from threading import Thread
import cv2
import time
import queue

class Camera:

  def __init__(self, url, numCameras):
    self.cap = cv2.VideoCapture(url)
    self.q = queue.Queue()
    self.numCameras = numCameras
    self.exit_flag = time.time()
    
    t = Thread(target=self.passiveRead)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def passiveRead(self):
    while True:
        if time.time() - self.exit_flag > 3: # after 3 seconds of inactivity stop the stream
            self.cap.release()
            break
        ret, frame = self.cap.read()
        if not ret:
            break
        if not self.q.empty():
            try:
                self.q.get_nowait()   # discard previous (unprocessed) frame
            except queue.Empty:
                pass
        self.q.put(frame)

  def getFrame(self):
    self.exit_flag = time.time()
    frame = self.q.get()
    # if more than one camera, resize the image
    if int(self.numCameras) > 1:
        frame = cv.resize(frame,None,fx=0.5,fy=0.5) 

    ret, frame = cv2.imencode('.jpg', frame)
    return frame
