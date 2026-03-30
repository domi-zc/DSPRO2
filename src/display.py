import cv2

def display_video_with_annotations(frame, landmarks, info={}):
    if landmarks:
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

    frame = draw_info_box(frame, info)

    cv2.imshow("video", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q") or key == 27:  # q or Esc to quit
        return True
    return False



def draw_info_box(frame, info):
    h, w = frame.shape[:2]

    # info in the box
    items = [
        ("Exercise", info.get("current_exercise", "-")),
        ("Reps", info.get("reps", "-")),
        ("State", info.get("state", "-")),
    ]
    lines = [f"{label}: {value}" for label, value in items]

    pad = 10
    line_h = 25
    box_w = 220
    box_h = pad * 2 + len(lines) * line_h

    x1, y1 = w - box_w - pad, pad
    x2, y2 = w - pad, y1 + box_h

    # drawing the box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 50), -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)

    # placing the lines in the box
    for i, text in enumerate(lines):
        y = y1 + pad + 18 + i * line_h
        x = x1 + pad
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return frame
