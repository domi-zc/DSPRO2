import cv2
from copy import deepcopy
import mediapipe as mp
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks.python import vision


def display_video_with_annotations(frame, landmarks):
    height, width, _ = frame.shape

    # Define the indices for the key points and the connections between them
    arm_indices = [11, 13, 15, 12, 14, 16]
    connections = [(11, 13), (13, 15), (12, 14), (14, 16)]

    # Draw the connection
    for start_idx, end_idx in connections:
        start = landmarks[start_idx]
        end = landmarks[end_idx]

        start_point = (int(start.x * width), int(start.y * height))
        end_point = (int(end.x * width), int(end.y * height))

        cv2.line(frame, start_point, end_point, (255, 255, 255), 2)

    # Draw the keypoints
    for idx in arm_indices:
        landmark = landmarks[idx]
        center = (int(landmark.x * width), (int(landmark.y * height)))
        cv2.circle(frame, center, 5, (0, 255, 0), -1)

    cv2.imshow("video", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:  # q or Esc to quit
        return "break"


    # if key_points is not None:
    #     selected = set(selected_landmarks)
    #     kp = deepcopy(key_points)
    #     # filter out only wanted landmarks for display
    #     for i, landmark in enumerate(kp):
    #         if i not in selected:
    #             landmark.visibility = 0
    #             landmark.presence = 0
    #     connections = [(a, b) for (a, b) in vision.PoseLandmarksConnections if a in selected and b in selected]

    #     # mp draws directly on the frame, so nothing needs to be returned
    #     mp_drawing.draw_landmarks(frame, kp)

    # cv2.imshow("video", frame)
