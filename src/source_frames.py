import cv2
import time

class SourceFrame:
    def __init__(self, start_time, index=0):
        self.cam = cv2.VideoCapture(index)
        self.start_time = start_time

    def get_frames(self):
        ret, frame = self.cam.read()
        current_time = int(time.time() * 1000)
        frame_timestamp = current_time - self.start_time
        if not ret:
            return None
        return frame_timestamp, frame
