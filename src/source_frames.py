import cv2
import time

class SourceFrame:
    def __init__(self, start_time, index=0):
        self.cam = cv2.VideoCapture(index)
        self.start_time = start_time

    @classmethod
    def from_video(cls, video_path, start_time):
        # Create a new class instance
        instance = cls.__new__(cls)

        # Load the video
        instance.cam = cv2.VideoCapture(video_path)
        instance.start_time = start_time
        if not instance.cam.isOpened():

            raise ValueError(f"Could not open video file: {video_path}")
        return instance

    def get_frames(self):
        ret, frame = self.cam.read()
        current_time = int(time.time() * 1000)
        frame_timestamp = current_time - self.start_time
        if not ret:
            return None
        return frame_timestamp, frame
