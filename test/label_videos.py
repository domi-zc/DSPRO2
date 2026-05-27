from pathlib import Path
import cv2


ROOT = Path(__file__).resolve().parents[1]

VIDEO_DIR = ROOT / "dataset" / "videos"
LABEL_DIR = ROOT / "dataset" / "labels"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

SMALL_JUMP = 10
BIG_JUMP = 20

KEY_LEFT = {81, 2424832, 65361, 63234}
KEY_RIGHT = {83, 2555904, 65363, 63235}

EXERCISE_BY_FOLDER = {
    "pushup": "pushups",
    "pushups": "pushups",
    "push_up": "pushups",
    "push_ups": "pushups",
    "pullup": "pullups",
    "pullups": "pullups",
    "pull_up": "pullups",
    "pull_ups": "pullups",
    "bicep_curl": "bicep_curls",
    "bicep_curls": "bicep_curls",
    "biceps_curl": "bicep_curls",
    "biceps_curls": "bicep_curls",
    "squat": "squats",
    "squats": "squats",
    "situp": "situps",
    "situps": "situps",
    "sit_up": "situps",
    "sit_ups": "situps",
}


def clean_name(name):
    return name.lower().replace("-", "_").replace(" ", "_")


def get_exercise_from_folder(video_path):
    relative_path = video_path.relative_to(VIDEO_DIR)

    for folder_name in reversed(relative_path.parts[:-1]):
        key = clean_name(folder_name)

        if key in EXERCISE_BY_FOLDER:
            return EXERCISE_BY_FOLDER[key]

    raise ValueError(f"Could not detect exercise from folder: {video_path}")


def get_video_files():
    return sorted(
        path for path in VIDEO_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )


def label_path(video_path):
    relative_path = video_path.relative_to(VIDEO_DIR).with_suffix(".txt")
    return LABEL_DIR / relative_path


def load_labels(path):
    if not path.exists():
        return []

    lines = path.read_text().splitlines()
    labels = []

    for line in lines[1:]:
        if not line.strip():
            continue

        exercise, time_sec = line.split(",", 1)
        labels.append((exercise.strip(), float(time_sec.strip())))

    return labels


def save_labels(path, video_path, labels):
    path.parent.mkdir(parents=True, exist_ok=True)

    labels = sorted(labels, key=lambda item: item[1])

    lines = [str(video_path)]
    for exercise, time_sec in labels:
        lines.append(f"{exercise}, {time_sec:.3f}")

    path.write_text("\n".join(lines) + "\n")
    print(f"Saved {path}")


def draw_text(frame, lines):
    y = 30

    for line in lines:
        cv2.putText(
            frame,
            line,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        y += 28


def label_video(video_path):
    try:
        exercise = get_exercise_from_folder(video_path)
    except ValueError as error:
        print(error)
        return "next"

    path = label_path(video_path)
    labels = load_labels(path)

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"Could not open {video_path}")
        return "next"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        print(f"Could not read frames from {video_path}")
        cap.release()
        return "next"

    frame_index = 0
    paused = True

    needs_seek = True
    frame = None

    while True:
        if needs_seek:
            frame_index = max(0, min(frame_index, total_frames - 1))

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()

            if not ok:
                break

            actual_frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            if actual_frame_index >= 0:
                frame_index = actual_frame_index

            needs_seek = False

        time_sec = frame_index / fps
        display = frame.copy()

        lines = [
            f"Video: {video_path.relative_to(VIDEO_DIR)}",
            f"Time: {time_sec:.3f}s | Frame: {frame_index}",
            f"Exercise from folder: {exercise}",
            f"State: {'PAUSED' if paused else 'PLAYING'}",
            "",
            "SPACE: add rep label + autosave",
            "U: undo last label + autosave",
            "Left/Right: +/- 1 frame",
            "A/D: +/- 10 frames",
            "J/L: +/- 20 frames",
            "P: play/pause",
            "S: save manually",
            "N: next video",
            "Q: quit without saving",
            "",
            "Last labels:",
        ]

        for exercise_name, label_time in labels[-5:]:
            lines.append(f"{exercise_name}, {label_time:.3f}")

        draw_text(display, lines)
        cv2.imshow("Label Videos", display)

        key = cv2.waitKeyEx(0 if paused else 30)

        if key == -1:
            if not paused:
                ok, next_frame = cap.read()

                if ok:
                    frame = next_frame

                    actual_frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                    if actual_frame_index >= 0:
                        frame_index = actual_frame_index
                    else:
                        frame_index += 1
                else:
                    paused = True
                    frame_index = total_frames - 1

            continue

        if key in {ord("q"), ord("Q")}:
            cap.release()
            return "quit"

        if key in {ord("n"), ord("N")}:
            cap.release()
            return "next"

        if key in {ord("s"), ord("S")}:
            save_labels(path, video_path, labels)

        elif key in {ord("p"), ord("P")}:
            paused = not paused

        elif key == 32:
            labels.append((exercise, time_sec))
            save_labels(path, video_path, labels)
            print(f"Added: {exercise}, {time_sec:.3f}")

        elif key in {ord("u"), ord("U")}:
            if labels:
                removed = labels.pop()
                save_labels(path, video_path, labels)
                print(f"Removed: {removed[0]}, {removed[1]:.3f}")

        elif key in KEY_LEFT:
            paused = True
            frame_index -= 1
            needs_seek = True

        elif key in KEY_RIGHT:
            paused = True
            frame_index += 1
            needs_seek = True

        elif key in {ord("a"), ord("A")}:
            paused = True
            frame_index -= SMALL_JUMP
            needs_seek = True

        elif key in {ord("d"), ord("D")}:
            paused = True
            frame_index += SMALL_JUMP
            needs_seek = True

        elif key in {ord("j"), ord("J")}:
            paused = True
            frame_index -= BIG_JUMP
            needs_seek = True

        elif key in {ord("l"), ord("L")}:
            paused = True
            frame_index += BIG_JUMP
            needs_seek = True

    cap.release()
    return "next"



def main():
    LABEL_DIR.mkdir(parents=True, exist_ok=True)

    videos = get_video_files()
    videos_to_label = [path for path in videos if not label_path(path).exists()]

    print(f"Found {len(videos)} video(s).")
    print(f"Need labels for {len(videos_to_label)} video(s).")

    for video_path in videos_to_label:
        result = label_video(video_path)

        if result == "quit":
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
