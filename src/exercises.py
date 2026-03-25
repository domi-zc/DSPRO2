from smoothing import smooth_angle
from abc import ABC, abstractmethod



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
        if not features:
            return
        
        # count right curls
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

        # count left curls
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



class PushUps(Exercise):
    def __init__(self, threshold_up=150, threshold_down=90):
        super().__init__(threshold_up, threshold_down)

        self._features_needed = {
            "keypoints": {
                "nose": 0,
                "left_shoulder": 11,
                "right_shoulder": 12,
                "left_elbow": 13,
                "right_elbow": 14,
                "left_wrist": 15,
                "right_wrist": 16,
            },
            "angles": ["right_elbow_angle", "left_elbow_angle"],
        }

        self.angle = None


    @property
    def features_needed(self):
        return self._features_needed

    def count_reps(self, features):
        if not features:
            return

        wrist_is_below_elbow = features["left_elbow"].y < features["left_wrist"].y and features["right_elbow"].y < features["right_wrist"].y
        if not wrist_is_below_elbow:
            return

        raw_angle = (features["right_elbow_angle"] + features["left_elbow_angle"]) / 2
        elbow_middle_y = (features["left_elbow"].y + features["right_elbow"].y) / 2
        nose_y = features["nose"].y

        if self.angle is not None:
            self.angle = smooth_angle(self.angle, raw_angle)
        else:
            self.angle = raw_angle

        if self.angle < self.threshold_up and self.state == "DOWN" and elbow_middle_y > nose_y:
            self.state = "UP"
            self.reps += 1

        if self.angle > self.threshold_down and self.state == "UP" and elbow_middle_y < nose_y:
            self.state = "DOWN"

    def display_count(self):
        print(f"Pushups reps: {self.reps}")



class Exercises():
    exercises = {"biceps_curls": BicepsCurls(), "push_ups": PushUps()}
