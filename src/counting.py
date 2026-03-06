

class Counter():
    def __init__(self):
        self.state = "UP"
        self.threshold_up = 30
        self.threshold_down = 130
        self.reps = 0
        
    def count_reps(self, angle, elbow, wrist):
        if angle < self.threshold_up and self.state == "DOWN" and elbow.y > wrist.y:
            self.state = "UP"
            self.reps += 1   
        
        if angle > self.threshold_down and self.state == "UP" and elbow.y < wrist.y:
            self.state = "DOWN"
        
        return self.reps
