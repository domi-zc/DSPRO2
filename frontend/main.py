from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import cv2
import sys
import os
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
src_dir = os.path.join(root_dir, "src")
sys.path.append(src_dir)

from pose_estimation import PoseEstimator
from feature_extraction import calculate_features
from exercises import Exercises


static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="landingpage.html")

@app.get("/webcam")
async def webcam(request: Request, exercise: str = "bicep_curl"):
    
    available_exercises = {}
    for key in Exercises.exercises.keys():
        display_name = key.replace("_", " ").title()
        available_exercises[key] = display_name
        
    if exercise not in available_exercises:
        exercise = "bicep_curl"
        
    exercise_name = available_exercises[exercise]
    
    return templates.TemplateResponse(
        request=request, 
        name="webcam.html", 
        context={
            "exercise_name": exercise_name, 
            "exercise_id": exercise,
            "available_exercises": available_exercises
        }
    )

EXERCISE_CONNECTIONS = {
    "bicep_curl": [(11, 13), (13, 15), (12, 14), (14, 16)],
    "pushup": [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12)], 
    "pullup": [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12)],
    "squat": [(23, 25), (25, 27), (24, 26), (26, 28), (23, 24)],
    "situp": [(12, 24), (24, 26), (26, 28), (11, 23), (23, 25), (25, 27)]
}

@app.websocket("/ws/video/{exercise_id}")
async def websocket_endpoint(websocket: WebSocket, exercise_id: str):
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
                needed_keypoints = current_exercise.features_needed["keypoints"].values()
                for idx in needed_keypoints:
                    response_data["landmarks"][str(idx)] = {
                        "x": lms[idx].x, 
                        "y": lms[idx].y
                    }

            await websocket.send_json(response_data)
            
    except WebSocketDisconnect:
        print("Client normal getrennt")
    except Exception as e:
        print(f"Fehler in der Verbindung: {e}")