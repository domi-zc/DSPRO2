from smoothing import smooth_angle
from abc import ABC, abstractmethod
import numpy as np

class Exercise(ABC):
    def __init__(self, threshold_up=45, threshold_down=130):
        self.threshold_up = threshold_up
        self.threshold_down = threshold_down
        self.state = "UP"
        self.reps = 0

    @property
    @abstractmethod
    def features_needed(self):
        pass

    @abstractmethod
    def count_reps(self, features):
        pass

    @abstractmethod
    def display_count(self):
        pass

    @abstractmethod
    def check_keypoint_visibility(self):
        pass

class BicepsCurls(Exercise):
    def __init__(self):
        super().__init__(threshold_up=45, threshold_down=130)

        self._features_needed = {
            "keypoints": {
                "right_shoulder": 12,
                "right_elbow": 14,
                "right_wrist": 16,
                "left_shoulder": 11,
                "left_elbow": 13,
                "left_wrist": 15,
            },
            "angles": ["right_elbow_angle", "left_elbow_angle"],
        }

        self.state_right = "UP"
        self.state_left = "UP"
        self.reps_right = 0
        self.angle_right = None
        self.reps_left = 0
        self.angle_left = None

    @property
    def features_needed(self):
        return self._features_needed

    def count_reps(self, features):
        # Exit on empty features
        if not features:
            return

        # Count right curls
        angle_right, elbow_right, wrist_right = features["right_elbow_angle"], features["right_elbow"], features["right_wrist"]

        if self.angle_right:
            self.angle_right = smooth_angle(self.angle_right, angle_right)
        else:
            self.angle_right = angle_right

        if self.angle_right < self.threshold_up and self.state_right == "DOWN" and elbow_right.y > wrist_right.y:
            self.state_right = "UP"
            self.reps_right += 1

        if self.angle_right > self.threshold_down and self.state_right == "UP" and elbow_right.y < wrist_right.y:
            self.state_right = "DOWN"

        # Count left curls
        angle_left, elbow_left, wrist_left = features["left_elbow_angle"], features["left_elbow"], features["left_wrist"]

        if self.angle_left:
            self.angle_left = smooth_angle(self.angle_left, angle_left)
        else:
            self.angle_left = angle_left

        if self.angle_left < self.threshold_up and self.state_left == "DOWN" and elbow_left.y > wrist_left.y:
            self.state_left = "UP"
            self.reps_left += 1

        if  self.angle_left > self.threshold_down and self.state_left == "UP" and elbow_left.y < wrist_left.y:
            self.state_left = "DOWN"


    def display_count(self):
        if self.angle_right:
           right_angle = f", Angle right: {int(self.angle_right)}°"
        else:
            right_angle = ""
        if self.angle_left:
           left_angle = f", Angle left: {int(self.angle_left)}°"
        else:
            left_angle = ""
        print(f"Biceps curls reps right: {self.reps_right}{right_angle}, reps left: {self.reps_left}{left_angle}")

    def check_keypoint_visibility(self):
        return super().check_keypoint_visibility()

class Squats(Exercise):
    def __init__(self, threshold_up=170, threshold_down=90):
        super().__init__(threshold_up, threshold_down)

        self._features_needed = {
        "keypoints": {
            "right_hip": 24,
            "right_knee": 26,
            "right_ankle": 28,
            "left_hip": 23,
            "left_knee": 25,
            "left_ankle": 27,
        },
        "angles": ["right_knee_angle", "left_knee_angle"]
        }

        self.current_angle = None
        self.state = "UP"
        self.reps = 0

    @property
    def features_needed(self):
        return self._features_needed

    def count_reps(self, features):
        # Exit on empty features
        if not features:
            return

        # Exit if the left or right body side is visible
        if not self.check_keypoint_visibility(features["right_hip"], features["right_knee"], features["right_ankle"]) \
            and not self.check_keypoint_visibility(features["left_hip"], features["left_knee"], features["left_ankle"]):
            return

        # Calculate the average angle of both legs
        average_angle = np.mean([features["right_knee_angle"], features["left_knee_angle"]])

        # Smooth the combined angle
        if self.current_angle:
            self.current_angle = smooth_angle(self.current_angle, average_angle)
        else:
            self.current_angle = average_angle

        # Extract the average X-coordinates
        average_hip_x = np.mean([features["right_hip"].x,  features["left_hip"].x])
        average_knee_x = np.mean([features["right_knee"].x,  features["left_knee"].x])
        average_ankle_x = np.mean([features["right_ankle"].x,  features["left_ankle"].x])

        # Check if the hip, knee and ankle are within 5% horizontal distance of each other
        alignment_threshold = 0.05
        is_aligned = (np.abs(average_hip_x - average_knee_x) < alignment_threshold and np.abs(average_knee_x - average_ankle_x) < alignment_threshold)

        if self.current_angle < self.threshold_down and self.state == "UP":
            self.state = "DOWN"

        if self.current_angle > self.threshold_up and self.state == "DOWN" and is_aligned:
            self.state = "UP"
            self.reps += 1

    def display_count(self):
        print(f"Knee angles: {self.current_angle}")
        print(f"Reps: {self.reps}")
        print(f"State: {self.state}")
        # print(f"Beneath threshold: {self.current_angle < self.threshold_down if self.current_angle else None}")

    def check_keypoint_visibility(self, hip, knee, ankle):
        """Checks if either the left or rights hip, knee and ankle visibility is over 90%."""
        print(f"Hip: {hip.visibility}, Knee {knee.visibility}, Ankle {ankle.visibility}")

        return hip.visibility > 0.9 and knee.visibility > 0.9 and ankle.visibility > 0.9



class Exercises():
    exercises = {"biceps_curls": BicepsCurls(), "squats": Squats()}
