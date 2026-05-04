import json
import time

from exercises import Squats, PushUps, PullUps, BicepsCurls, SitUps


class Workout:
    def __init__(self, json_path):
        self.workout_name = ""
        self.steps = []
        self.current_step_index = 0
        self.rest_until = None
        self.finished = False

        self.load_workout(json_path)

    def load_workout(self, json_path):
        exercise_classes = {
            "Squats": Squats,
            "Push-ups": PushUps,
            "Pull-ups": PullUps,
            "Bicep Curls": BicepsCurls,
            "Situps": SitUps,
        }

        with open(json_path, "r") as file:
            workout_data = json.load(file)

        self.workout_name = workout_data["workout_name"]

        for exercise_data in workout_data["exercises"]:
            name = exercise_data["name"]
            sets = exercise_data["sets"]
            reps = exercise_data["reps"]
            rest_after_seconds = exercise_data["rest_after_seconds"]

            exercise_class = exercise_classes[name]

            for set_number in range(1, sets + 1):
                self.steps.append({
                    "exercise": exercise_class(),
                    "name": name,
                    "set_number": set_number,
                    "total_sets": sets,
                    "target_reps": reps,
                    "rest_after_seconds": rest_after_seconds,
                })

    def get_current_exercise(self):
        if self.finished or self.is_resting():
            return None

        return self.steps[self.current_step_index]["exercise"]

    def update(self, features):
        if self.finished:
            return

        if self.is_resting():
            if self.current_time_ms() >= self.rest_until:
                self.go_to_next_step()
            return

        current_step = self.steps[self.current_step_index]
        exercise = current_step["exercise"]

        exercise.count_reps(features)

        if self.get_reps(exercise) >= current_step["target_reps"]:
            rest_seconds = current_step["rest_after_seconds"]

            if rest_seconds > 0:
                self.rest_until = self.current_time_ms() + rest_seconds * 1000
            else:
                self.go_to_next_step()

    def go_to_next_step(self):
        self.rest_until = None
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.finished = True

    def skip(self):
        if not self.finished:
            self.go_to_next_step()

    def is_resting(self):
        return self.rest_until is not None

    def get_reps(self, exercise):
        if hasattr(exercise, "reps_left") and hasattr(exercise, "reps_right"):
            return min(exercise.reps_left, exercise.reps_right)

        return exercise.reps

    def get_display_info(self):
        if self.finished:
            return {
                "current_exercise": "Workout complete",
                "reps": "-",
                "state": "DONE",
            }

        current_step = self.steps[self.current_step_index]
        exercise = current_step["exercise"]

        if self.is_resting():
            seconds_left = max(0, int((self.rest_until - self.current_time_ms()) / 1000))

            return {
                "current_exercise": "Rest",
                "reps": f"{seconds_left}s",
                "state": "REST",
            }

        return {
            "current_exercise": exercise.name,
            "reps": f"{self.get_reps(exercise)}/{current_step['target_reps']}",
            "state": f"Set {current_step['set_number']}/{current_step['total_sets']}",
        }

    def current_time_ms(self):
        return int(time.time() * 1000)