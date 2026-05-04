from pose_estimation import PoseEstimator
from source_frames import SourceFrame
from display import display_video_with_annotations
from smoothing import smooth_angle
from angle import calculate_angle
from feature_extraction import calculate_features
from exercises import Exercises
from workout import Workout

import time
import cv2


def main():
    print('---------- Running ----------')
    source_frame = SourceFrame(start_time=int(time.time() * 1000))
    # source_frame = SourceFrame.from_video("videos/situps.mp4", start_time=int(time.time() * 1000))

    workout = Workout("workouts/test_workout.json")

    print(f"---------- Loaded workout: {workout.workout_name} ----------")
    print('---------- Received frames ----------')

    pose_estimator = PoseEstimator()
    landmarks = None

    while True:
        frame_data = source_frame.get_frames()
        if frame_data is None:
            print("Failed to read frame from camera.")
            continue

        frame_timestamp, frame = frame_data
        result = pose_estimator.estimate_pose(frame_timestamp, frame)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

        current_exercise = workout.get_current_exercise()

        if current_exercise is not None:
            features = calculate_features(result, current_exercise.features_needed)
            workout.update(features)
        else:
            workout.update({})

        exercise_info_specs = workout.get_display_info()
        display_video_with_annotations(frame, landmarks, exercise_info_specs)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

        if key == ord("s"):
            workout.skip()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
