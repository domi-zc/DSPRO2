from pose_estimation import PoseEstimator
from source_frames import SourceFrame
from display import display_video_with_annotations
from counting import Counter
from smoothing import smooth_angle
from angle import calculate_angle
import time


def main():
    print('---------- Running ----------')
    source_frame = SourceFrame(start_time=int(time.time() * 1000))

    print('---------- Received frames ----------')
    pose_estimator = PoseEstimator()

    counter = Counter()
    old_angle = None

    while True:
        frame_timestamp, frame = source_frame.get_frames()
        result = pose_estimator.estimate_pose(frame_timestamp, frame)
        landmarks = result.pose_landmarks[0]

        if result.pose_landmarks:
            shoulder, elbow, wrist = landmarks[12], landmarks[14], landmarks[16]
            angle = calculate_angle(shoulder, elbow, wrist)

            angle = smooth_angle(old_angle, angle)
            old_angle = angle
            reps = counter.count_reps(angle, elbow, wrist)
            print(f"Reps: {reps}, Angle: {int(angle)}°")

        # Arm keypoints
        if display_video_with_annotations(frame, landmarks):
            break

if __name__ == "__main__":
    main()
