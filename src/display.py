import cv2
import mediapipe as mp
from copy import deepcopy

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
    
def display_video_with_annotations(frame, key_points, selected_landmarks=range(33)):
    if key_points is not None:
        selected = set(selected_landmarks)
        kp = deepcopy(key_points)
        # filter out only wanted landmarks for display
        for i, landmark in enumerate(kp.landmark):
            if i not in selected:
                landmark.visibility = 0
                landmark.presence = 0
        connections = [(a, b) for (a, b) in mp_pose.POSE_CONNECTIONS if a in selected and b in selected]
        
        # mp draws directly on the frame, so nothing needs to be returned
        mp_drawing.draw_landmarks(frame, kp, connections)
    
    cv2.imshow("video", frame)
      
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:  # q or Esc to quit
        return "break"