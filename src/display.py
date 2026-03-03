import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
    
def display_video_with_annotations(frame, key_points):
    # mp draws directly on the frame, so nothing needs to be returned
    if key_points is not None:
        mp_drawing.draw_landmarks(frame, key_points, mp_pose.POSE_CONNECTIONS)
    
    cv2.imshow("video", frame)
      
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:  # q or Esc to quit
        return "break"