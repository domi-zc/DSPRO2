from smoothing import smooth_angle


class BicepsCurlsRight():
    def __init__(self):
        self.features_needed = {"keypoints": {"right_shoulder": 12, "right_elbow": 14, "right_wrist": 16}, "angles": ["right_elbow_angle"]}
        self.state = "UP"
        self.threshold_up = 30
        self.threshold_down = 130
        self.reps = 0
        self.angle = None
        
    def count_reps(self, features):
        if not features:
            return self.reps
        angle, elbow, wrist = features["right_elbow_angle"], features["right_elbow"], features["right_wrist"]
        if self.angle:
            self.angle = smooth_angle(self.angle, angle)
        else:
            self.angle = angle
            
        
        if angle < self.threshold_up and self.state == "DOWN" and elbow.y > wrist.y:
            self.state = "UP"
            self.reps += 1   
        
        if angle > self.threshold_down and self.state == "UP" and elbow.y < wrist.y:
            self.state = "DOWN"
        
        return self.reps

    def display_count(self):
        if self.angle:
            print(f"Reps biceps curls right: {self.reps}, Angle: {int(self.angle)}°")
        else:
            print(f"Reps biceps curls right: {self.reps}")


class BicepsCurlsLeft():
    def __init__(self):
        self.features_needed = {"keypoints": {"left_shoulder": 11, "left_elbow": 13, "left_wrist": 15}, "angles": ["left_elbow_angle"]}
        self.state = "UP"
        self.threshold_up = 30
        self.threshold_down = 130
        self.reps = 0
        self.angle = None
        
    def count_reps(self, features):
        if not features:
            return self.reps
        angle, elbow, wrist = features["left_elbow_angle"], features["left_elbow"], features["left_wrist"]
        if self.angle:
            self.angle = smooth_angle(self.angle, angle)
        else:
            self.angle = angle
            
        
        if angle < self.threshold_up and self.state == "DOWN" and elbow.y > wrist.y:
            self.state = "UP"
            self.reps += 1   
        
        if angle > self.threshold_down and self.state == "UP" and elbow.y < wrist.y:
            self.state = "DOWN"
        
        return self.reps

    def display_count(self):
        if self.angle:
            print(f"Reps biceps curls left: {self.reps}, Angle: {int(self.angle)}°")
        else:
            print(f"Reps biceps curls left: {self.reps}")



class Exercises():
    exercises = {"biceps_curls_right": BicepsCurlsRight(), "biceps_curls_left": BicepsCurlsLeft()}