import mediapipe as mp
import cv2

class PoseEstimator:
    def __init__(self):
        self.pose = mp.solutions.pose.Pose()
        
    def estimate_pose(self, frames):
        frames = cv2.cvtColor(frames, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frames)
        return results
