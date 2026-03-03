import cv2


class SourceFrame:
    def __init__(self, index=0):
        self.cam = cv2.VideoCapture(index)

    def get_frames(self):
        ret, frame = self.cam.read()
        if not ret:
            return None
        return frame