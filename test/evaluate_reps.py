from pathlib import Path
from collections import defaultdict
from contextlib import redirect_stdout
import os
import sys
import cv2


ROOT = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from pose_estimation import PoseEstimator
from feature_extraction import calculate_features
from exercises import PushUps, PullUps, BicepsCurls, Squats, SitUps


VIDEO_DIR = ROOT / "dataset" / "videos"
LABEL_DIR = ROOT / "dataset" / "labels"
PREDICTION_DIR = ROOT / "dataset" / "predictions"
MODEL_PATH = ROOT / "mediapipe" / "pose_landmarker.task"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
TIME_MARGINS = [0.25, 0.5, 1.0]

EXERCISE_CLASSES = {
    "pushup": PushUps,
    "pushups": PushUps,
    "push_up": PushUps,
    "push_ups": PushUps,
    "pullup": PullUps,
    "pullups": PullUps,
    "pull_up": PullUps,
    "pull_ups": PullUps,
    "bicep_curl": BicepsCurls,
    "bicep_curls": BicepsCurls,
    "biceps_curl": BicepsCurls,
    "biceps_curls": BicepsCurls,
    "squat": Squats,
    "squats": Squats,
    "situp": SitUps,
    "situps": SitUps,
    "sit_up": SitUps,
    "sit_ups": SitUps,
}


def clean_name(name):
    return name.lower().replace("-", "_").replace(" ", "_")


def get_video_files():
    return sorted(
        path for path in VIDEO_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )


def label_path(video_path):
    relative_path = video_path.relative_to(VIDEO_DIR).with_suffix(".txt")
    return LABEL_DIR / relative_path


def prediction_path(video_path):
    relative_path = video_path.relative_to(VIDEO_DIR).with_suffix(".txt")
    return PREDICTION_DIR / relative_path


def read_rep_file(path):
    if not path.exists():
        return []

    lines = path.read_text().splitlines()
    reps = []

    for line in lines[1:]:
        if not line.strip():
            continue

        exercise, time_sec = line.split(",", 1)

        reps.append({
            "exercise": exercise.strip(),
            "time": float(time_sec.strip()),
        })

    return reps


def write_rep_file(path, video_path, reps):
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [str(video_path)]

    for rep in reps:
        lines.append(f"{rep['exercise']}, {rep['time']:.3f}")

    path.write_text("\n".join(lines) + "\n")


def make_exercise(exercise_name):
    key = clean_name(exercise_name.strip())

    if key not in EXERCISE_CLASSES:
        raise ValueError(f"Unknown exercise in label file: {exercise_name}")

    return EXERCISE_CLASSES[key]()


def get_rep_count(exercise):
    if hasattr(exercise, "reps_left") and hasattr(exercise, "reps_right"):
        return min(exercise.reps_left, exercise.reps_right)

    return exercise.reps


def get_exercise_from_labels(labels):
    if not labels:
        return None

    exercise = labels[0]["exercise"]

    for label in labels:
        if label["exercise"] != exercise:
            print("Warning: one video should only contain one exercise.")

    return exercise


def predict_video(video_path, exercise_name):
    exercise = make_exercise(exercise_name)
    pose_estimator = PoseEstimator(model_path=str(MODEL_PATH))

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    frame_index = 0
    predictions = []

    with open(os.devnull, "w") as devnull:
        while True:
            ok, frame = cap.read()

            if not ok:
                break

            timestamp_ms = int(frame_index * 1000 / fps)
            time_sec = timestamp_ms / 1000

            result = pose_estimator.estimate_pose(timestamp_ms, frame)
            features = calculate_features(result, exercise.features_needed)

            before = get_rep_count(exercise)

            with redirect_stdout(devnull):
                exercise.count_reps(features)

            after = get_rep_count(exercise)

            if after > before:
                predictions.append({
                    "exercise": exercise_name,
                    "time": time_sec,
                })

            frame_index += 1

    cap.release()
    return predictions


def create_predictions():
    prediction_files = []

    for video_path in get_video_files():
        labels = read_rep_file(label_path(video_path))
        exercise_name = get_exercise_from_labels(labels)
        current_prediction_path = prediction_path(video_path)

        if exercise_name is None:
            print(f"Skipping {video_path.relative_to(VIDEO_DIR)}: no label file or no labels.")
            continue

        if current_prediction_path.exists():
            print(f"Using existing prediction for {video_path.relative_to(VIDEO_DIR)}")
            prediction_files.append(video_path)
            continue

        print(f"Predicting {video_path.relative_to(VIDEO_DIR)} as {exercise_name}...")

        predictions = predict_video(video_path, exercise_name)
        write_rep_file(current_prediction_path, video_path, predictions)

        prediction_files.append(video_path)

    return prediction_files


def match_reps(labels, predictions, margin):
    candidates = []

    for label_index, label in enumerate(labels):
        for pred_index, pred in enumerate(predictions):
            if label["exercise"] != pred["exercise"]:
                continue

            error = abs(label["time"] - pred["time"])

            if error <= margin:
                candidates.append((error, label_index, pred_index))

    candidates.sort()

    used_labels = set()
    used_predictions = set()
    matches = []

    for error, label_index, pred_index in candidates:
        if label_index in used_labels:
            continue

        if pred_index in used_predictions:
            continue

        used_labels.add(label_index)
        used_predictions.add(pred_index)
        matches.append((label_index, pred_index))

    false_negatives = len(labels) - len(used_labels)
    false_positives = len(predictions) - len(used_predictions)
    true_positives = len(matches)

    return true_positives, false_positives, false_negatives


def safe_divide(a, b):
    if b == 0:
        return 0.0

    return a / b


def metrics(tp, fp, fn):
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)

    return precision, recall, f1


def evaluate(files):
    print("\nOverall results")
    print("-" * 78)
    print(f"{'Margin':>10} {'TP':>6} {'FP':>6} {'FN':>6} {'Precision':>12} {'Recall':>12} {'F1':>12}")
    print("-" * 78)

    for margin in TIME_MARGINS:
        total_tp = 0
        total_fp = 0
        total_fn = 0

        per_exercise = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

        for video_path in files:
            labels = read_rep_file(label_path(video_path))
            predictions = read_rep_file(prediction_path(video_path))

            tp, fp, fn = match_reps(labels, predictions, margin)

            total_tp += tp
            total_fp += fp
            total_fn += fn

            exercise_name = labels[0]["exercise"]

            per_exercise[exercise_name]["tp"] += tp
            per_exercise[exercise_name]["fp"] += fp
            per_exercise[exercise_name]["fn"] += fn

        precision, recall, f1 = metrics(total_tp, total_fp, total_fn)

        print(
            f"{margin:>10.2f} "
            f"{total_tp:>6} "
            f"{total_fp:>6} "
            f"{total_fn:>6} "
            f"{precision:>12.3f} "
            f"{recall:>12.3f} "
            f"{f1:>12.3f}"
        )

        print(f"\nPer exercise for margin ±{margin:.2f}s")
        print("-" * 78)

        for exercise_name, values in sorted(per_exercise.items()):
            precision, recall, f1 = metrics(
                values["tp"],
                values["fp"],
                values["fn"],
            )

            print(
                f"{exercise_name:<15} "
                f"TP={values['tp']:<4} "
                f"FP={values['fp']:<4} "
                f"FN={values['fn']:<4} "
                f"P={precision:.3f} "
                f"R={recall:.3f} "
                f"F1={f1:.3f}"
            )

        print("\n" * 2)


def main():
    PREDICTION_DIR.mkdir(parents=True, exist_ok=True)

    files = create_predictions()

    if not files:
        print("No videos with labels found.")
        return

    evaluate(files)


if __name__ == "__main__":
    main()
