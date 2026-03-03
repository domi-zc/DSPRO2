from pose_estimation import PoseEstimator
from source_frames import SourceFrame
from display import display_video_with_annotations


def main():
    sf = SourceFrame()
    pe = PoseEstimator()
    
    while True:
        frame = sf.get_frames()
        result = pe.estimate_pose(frame)
        
        if display_video_with_annotations(frame, result.pose_landmarks):
            break
        
if __name__ == "__main__":
    main()
