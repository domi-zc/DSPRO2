from angle import calculate_angle


def calculate_features(key_points, features_needed):
    if not key_points.pose_landmarks:
        return
    pose_landmarks = key_points.pose_landmarks[0]
    
    if not pose_landmarks:
        return
    features = {}
    for kp, idx in features_needed["keypoints"].items():
        # add features that are needed to the features list
        # e.g. features["right_shoulder"] = pose_landmarks[12] -> {'right_shoulder': NormalizedLandmark(x=0.16080570220947266, y=0.053416430950164795, z=-0.7033865451812744, visibility=0.9922491312026978, presence=0.9542466998100281, name=None)}
        features[kp] = pose_landmarks[idx]
        print(features)
    
    # calculate the needed feature angles
    if "right_elbow_angle" in features_needed["angles"]:
        angle = calculate_angle(
            pose_landmarks[features_needed["keypoints"]["right_shoulder"]],
            pose_landmarks[features_needed["keypoints"]["right_elbow"]],
            pose_landmarks[features_needed["keypoints"]["right_wrist"]]
            )
        features["right_elbow_angle"] = angle
    
    if "left_elbow_angle" in features_needed["angles"]:
        angle = calculate_angle(
            pose_landmarks[features_needed["keypoints"]["left_shoulder"]],
            pose_landmarks[features_needed["keypoints"]["left_elbow"]],
            pose_landmarks[features_needed["keypoints"]["left_wrist"]]
            )
        features["left_elbow_angle"] = angle
    
    return features
