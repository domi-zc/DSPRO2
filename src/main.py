from pose_estimation import PoseEstimator
from source_frames import SourceFrame
from display import display_video_with_annotations
from smoothing import smooth_angle
from angle import calculate_angle
from feature_extraction import calculate_features
from exercises import Exercises
import time


def main():
    print('---------- Running ----------')
    source_frame = SourceFrame(start_time=int(time.time() * 1000))

    print('---------- Received frames ----------')
    pose_estimator = PoseEstimator()

    landmarks = None

    exercise_name = "biceps_curls_right"
    current_exercise = Exercises.exercises[exercise_name]

    while True:
        frame_data = source_frame.get_frames()
        if frame_data is None:
            print("Failed to read frame from camera.")
            continue

        frame_timestamp, frame = frame_data
        result = pose_estimator.estimate_pose(frame_timestamp, frame)

        features = calculate_features(result, current_exercise.features_needed)
        reps = current_exercise.count_reps(features)

        current_exercise.display_count()

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]
        # Arm keypoints
        if display_video_with_annotations(frame, landmarks):
            break

if __name__ == "__main__":
    main()
