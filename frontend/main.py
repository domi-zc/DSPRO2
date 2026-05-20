import os
import sys
import json
import cv2
import numpy as np

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
src_dir = os.path.join(root_dir, "src")
sys.path.append(src_dir)

from pose_estimation import PoseEstimator
from feature_extraction import calculate_features
from exercises import Exercises
from workout import Workout

EXERCISE_CONNECTIONS = {
    "bicep_curl": [(11, 13), (13, 15), (12, 14), (14, 16)],
    "pushup": [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12)], 
    "pullup": [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12)],
    "squat": [(23, 25), (25, 27), (24, 26), (26, 28), (23, 24)],
    "situp": [(12, 24), (24, 26), (26, 28), (11, 23), (23, 25), (25, 27)]
}

WORKOUT_NAME_MAP = {
    "Bicep Curls": "bicep_curl",
    "Push-ups": "pushup",
    "Pull-ups": "pullup",
    "Squats": "squat",
    "SitUps": "situp"
}

static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/")
async def index(request: Request):
    """
    Renders the initial landing page.
    """
    return templates.TemplateResponse(request=request, name="landingpage.html")


@app.get("/training")
async def training(request: Request):
    """
    Loads all available JSON workouts and exercises for the selection screen.
    """
    workouts_dir = os.path.join(root_dir, "workouts")
    workouts = []
    
    # Parse available workouts
    if os.path.exists(workouts_dir):
        for file_name in os.listdir(workouts_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(workouts_dir, file_name)
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        data["id"] = file_name.replace(".json", "")
                        workouts.append(data)
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")

    # Parse available individual exercises
    workouts.sort(key=lambda x: x.get("area", "").lower())

    raw_exercises = {
        key: key.replace("_", " ").title() 
        for key in Exercises.exercises.keys()
    }
    available_exercises = dict(sorted(raw_exercises.items(), key=lambda item: item[1]))
        
    return templates.TemplateResponse(
        request=request, 
        name="training.html", 
        context={
            "workouts": workouts,
            "exercises": available_exercises
        }
    )


@app.get("/exercise/{exercise_id}")
async def exercise_page(request: Request, exercise_id: str):
    """
    Renders the UI for a single infinite-rep exercise.
    """
    raw_exercises = {
        key: key.replace("_", " ").title() 
        for key in Exercises.exercises.keys()
    }
    available_exercises = dict(sorted(raw_exercises.items(), key=lambda item: item[1]))
    
    # Fallback if invalid ID is passed
    if exercise_id not in Exercises.exercises:
        exercise_id = "bicep_curl"
        
    exercise_name = exercise_id.replace("_", " ").title()
    
    return templates.TemplateResponse(
        request=request, 
        name="exercise.html", 
        context={
            "exercise_name": exercise_name, 
            "exercise_id": exercise_id,
            "available_exercises": available_exercises
        }
    )


@app.get("/workout/{workout_id}")
async def workout_page(request: Request, workout_id: str):
    """
    Renders the UI for a structured JSON workout routine.
    """
    file_path = os.path.join(root_dir, "workouts", f"{workout_id}.json")
    
    if not os.path.exists(file_path):
        return RedirectResponse(url="/training")
        
    with open(file_path, "r") as f:
        workout_data = json.load(f)
        
    return templates.TemplateResponse(
        request=request, 
        name="workout.html", 
        context={
            "workout": workout_data,
            "workout_id": workout_id
        }
    )


@app.websocket("/ws/workout/{workout_id}")
async def websocket_workout_endpoint(websocket: WebSocket, workout_id: str):
    """
    Handles real-time video processing, state management, and the Up Next queue for workouts.
    """
    await websocket.accept()
    
    model_path = os.path.join(root_dir, 'mediapipe', 'pose_landmarker.task')
    pose_estimator = PoseEstimator(model_path=model_path)
    
    file_path = os.path.join(root_dir, "workouts", f"{workout_id}.json")
    workout = Workout(file_path)
    
    # Prevent rest timer from triggering after the final exercise in the workout
    if workout.steps and len(workout.steps) > 0:
        workout.steps[-1]["rest_after_seconds"] = 0
    
    timestamp_ms = 0
    
    try:
        while True:
            image_bytes = await websocket.receive_bytes()
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            timestamp_ms += 33
            result = pose_estimator.estimate_pose(timestamp_ms, frame)
            
            current_exercise = workout.get_current_exercise()
            connections = []
            features = {}
            
            # Process exercise state and skeletal connections
            if current_exercise is not None:
                ex_name_lower = current_exercise.name.lower()
                
                safe_map = {k.lower(): v for k, v in WORKOUT_NAME_MAP.items()}
                
                mapped_name = safe_map.get(ex_name_lower, "")
                connections = EXERCISE_CONNECTIONS.get(mapped_name, [])
                
                features = calculate_features(result, current_exercise.features_needed)
                workout.update(features)
            else:
                workout.update({}) # Handles resting or finished states

            raw_stats = workout.get_display_info()
            
            pose_state = None
            reps_left = None
            reps_right = None
            state_left = None
            state_right = None

            if current_exercise is not None:
                pose_state = getattr(current_exercise, 'state', getattr(current_exercise, 'state_right', None))
                
                if hasattr(current_exercise, 'reps_left'):
                    reps_left = current_exercise.reps_left
                    reps_right = current_exercise.reps_right
                    state_left = current_exercise.state_left
                    state_right = current_exercise.state_right

            up_next = []
            if not workout.finished:
                current_index = workout.current_step_index
                
                if workout.is_resting():
                    upcoming_idx = current_index + 1
                    
                    if upcoming_idx < len(workout.steps):
                        raw_stats["current_exercise"] = f"Rest"
                    
                    start_idx = upcoming_idx
                else:
                    start_idx = current_index + 1
                
                for i in range(start_idx, min(start_idx + 3, len(workout.steps))):
                    next_step = workout.steps[i]
                    up_next.append({
                        "name": next_step["name"],
                        "reps": next_step["target_reps"],
                        "set": f"Set {next_step['set_number']}/{next_step['total_sets']}"
                    })
            
            stats = {
                **raw_stats, 
                "up_next": up_next, 
                "pose_state": pose_state,
                "reps_left": reps_left,
                "reps_right": reps_right,
                "state_left": state_left,
                "state_right": state_right
            }

            response_data = {
                "stats": stats,
                "connections": connections,
                "landmarks": {}
            }

            # Map the precise body landmarks required for this exercise
            if result.pose_landmarks and current_exercise is not None:
                lms = result.pose_landmarks[0]
                
                needed_keypoints = set(current_exercise.features_needed["keypoints"].values())
                
                for start_idx, end_idx in connections:
                    needed_keypoints.add(start_idx)
                    needed_keypoints.add(end_idx)
                
                for idx in needed_keypoints:
                    response_data["landmarks"][str(idx)] = {
                        "x": lms[idx].x, 
                        "y": lms[idx].y
                    }

            await websocket.send_json(response_data)
            
    except WebSocketDisconnect:
        print("Workout client disconnected normally.")
    except Exception as e:
        print(f"Workout connection error: {e}")


@app.websocket("/ws/exercise/{exercise_id}")
async def websocket_endpoint(websocket: WebSocket, exercise_id: str):
    """
    Handles real-time video processing for endless single-exercise loops.
    """
    await websocket.accept()
    
    model_path = os.path.join(root_dir, 'mediapipe', 'pose_landmarker.task')
    pose_estimator = PoseEstimator(model_path=model_path)
    
    if exercise_id not in Exercises.exercises:
        exercise_id = "bicep_curl"
    
    exercise_template = Exercises.exercises[exercise_id]
    current_exercise = type(exercise_template)()
    
    connections = EXERCISE_CONNECTIONS.get(exercise_id, [])
    
    timestamp_ms = 0
    
    try:
        while True:
            image_bytes = await websocket.receive_bytes()
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            timestamp_ms += 33
            
            result = pose_estimator.estimate_pose(timestamp_ms, frame)
            features = calculate_features(result, current_exercise.features_needed)
            current_exercise.count_reps(features)

            # Format the output stats based on the exercise requirements
            stats = {}
            if exercise_id == "bicep_curl":
                stats = {
                    "Reps (Rechts)": current_exercise.reps_right,
                    "State (Rechts)": current_exercise.state_right,
                    "Reps (Links)": current_exercise.reps_left,
                    "State (Links)": current_exercise.state_left
                }
            elif exercise_id == "squat":
                stats = {
                    "Reps": current_exercise.reps,
                    "State": current_exercise.state,
                    "Angle": f"{int(current_exercise.current_angle)}°" if current_exercise.current_angle else "-"
                }
            else:
                stats = {
                    "Reps": current_exercise.reps,
                    "State": current_exercise.state
                }

            response_data = {
                "stats": stats,
                "connections": connections,
                "landmarks": {}
            }

            if result.pose_landmarks:
                lms = result.pose_landmarks[0]
                
                needed_keypoints = set(current_exercise.features_needed["keypoints"].values())
                for start_idx, end_idx in connections:
                    needed_keypoints.add(start_idx)
                    needed_keypoints.add(end_idx)
                
                for idx in needed_keypoints:
                    response_data["landmarks"][str(idx)] = {
                        "x": lms[idx].x, 
                        "y": lms[idx].y
                    }

            await websocket.send_json(response_data)
            
    except WebSocketDisconnect:
        print("Exercise client disconnected normally.")
    except Exception as e:
        print(f"Exercise connection error: {e}")