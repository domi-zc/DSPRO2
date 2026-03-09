import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np

class PoseEstimator:
    def __init__(self, model_path='./mediapipe/pose_landmarker.task'):
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = vision.PoseLandmarker
        PoseLandmarkerOptions = vision.PoseLandmarkerOptions
        VisionRunningMode = vision.RunningMode

        # Create PoseLandmarker with video mode
        options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO)

        self.landmarker = PoseLandmarker.create_from_options(options)

    def estimate_pose(self, timestamp, frame):
        # Convert the frame to an 8-bit integer if necessary
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)

        # Convert the frame to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.landmarker.detect_for_video(mp_image, timestamp)

        return result
