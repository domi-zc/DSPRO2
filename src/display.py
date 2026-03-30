import cv2

indices = {
    "bicep_curls": {
        "points": [11, 13, 15, 12, 14, 16],
        "connections": [(11, 13), (13, 15), (12, 14), (14, 16)]
    },
    "squats": {
        "points": [23, 25, 27, 24, 26, 28],
        "connections": [(23, 25), (25, 27), (24, 26), (26, 28)]
    }
}

def display_video_with_annotations(frame, landmarks):
    if landmarks:
        height, width, _ = frame.shape

        # Define the indices for the key points and the connections between them
        points = indices["squats"]["points"]
        connections = indices["squats"]["connections"]

        # Draw the connection
        for start_idx, end_idx in connections:
            start = landmarks[start_idx]
            end = landmarks[end_idx]

            start_point = (int(start.x * width), int(start.y * height))
            end_point = (int(end.x * width), int(end.y * height))

            cv2.line(frame, start_point, end_point, (255, 255, 255), 2)

        # Draw the keypoints
        for idx in points:
            landmark = landmarks[idx]
            center = (int(landmark.x * width), (int(landmark.y * height)))
            cv2.circle(frame, center, 5, (0, 255, 0), -1)

    cv2.imshow("video", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:  # q or Esc to quit
        return True
    return False
