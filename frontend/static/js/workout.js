const video = document.querySelector('.tvc-camera-container-video video');
const outputCanvas = document.querySelector('.tvc-camera-container-video canvas');
const ctx = outputCanvas.getContext('2d');

const exDisplay = document.getElementById('current-exercise-display');
const repsDisplay = document.getElementById('current-reps-display');
const upNextList = document.getElementById('up-next-list');
const repsContainer = document.querySelector('.tvc-reps-counter-left');

// Hidden canvas for capturing frame blobs to send to the backend
const hiddenCanvas = document.createElement('canvas');
hiddenCanvas.width = 1280;
hiddenCanvas.height = 720;
const hiddenCtx = hiddenCanvas.getContext('2d');

// WebSocket & Camera Configuration
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/workout/${currentWorkoutId}`);
ws.binaryType = "blob";

/**
 * Captures the current video frame, draws it to the hidden canvas, 
 * compresses it to JPEG, and sends it to the backend via WebSockets.
 */
function sendFrame() {
    if (ws.readyState === WebSocket.OPEN && video.readyState === video.HAVE_ENOUGH_DATA) {
        hiddenCtx.drawImage(video, 0, 0, hiddenCanvas.width, hiddenCanvas.height);
        hiddenCanvas.toBlob((blob) => { if (blob) ws.send(blob); }, 'image/jpeg', 0.7);
    }
}

ws.onopen = () => {
    navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 }, height: { ideal: 720 } } })
    .then(stream => {
        video.srcObject = stream;
        video.onloadedmetadata = () => {
            outputCanvas.width = video.videoWidth;
            outputCanvas.height = video.videoHeight;
            hiddenCanvas.width = video.videoWidth;
            hiddenCanvas.height = video.videoHeight;
        };
        video.onplaying = sendFrame;
    }).catch(err => console.error("Camera access error:", err));
};

// UI Updates & Pose Rendering
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Update the Live Stats Overlay
    if (data.stats) {
        exDisplay.innerText = data.stats.current_exercise || "-";
        
        if (data.stats.state === "DONE") {
            repsDisplay.innerText = "DONE";
            if (repsContainer) repsContainer.classList.remove('tvc-up', 'tvc-down');
        } else {
            repsDisplay.innerText = data.stats.reps || "-";
            
            const displayState = data.stats.pose_state; 
            if (displayState && repsContainer) {
                repsContainer.classList.remove('tvc-up', 'tvc-down');
                const stateLower = displayState.toLowerCase();
                if (stateLower === 'up') repsContainer.classList.add('tvc-up');
                else if (stateLower === 'down') repsContainer.classList.add('tvc-down');
            }
        }
        
        if (data.stats.up_next && upNextList) {
            upNextList.innerHTML = ''; 
            
            if (data.stats.up_next.length === 0) {
                upNextList.innerHTML = '<div class="tvc-workout-list-item" style="text-align:center; color:#888;">Get your protein!<div>';
            } else {
                data.stats.up_next.forEach(step => {
                    const item = document.createElement('div');
                    item.className = 'tvc-workout-list-item';
                    item.innerHTML = `
                        <div class="tvc-wli-header">
                            <strong>${step.name}</strong>
                            <span>${step.set}</span>
                        </div>
                        <div class="tvc-wli-details">
                            ${step.reps} Reps
                        </div>
                    `;
                    upNextList.appendChild(item);
                });
            }
        }
    }

    // Paint the camera feed to the visible canvas
    ctx.drawImage(hiddenCanvas, 0, 0, outputCanvas.width, outputCanvas.height);

    // Render pose skeletons over the live feed
    if (Object.keys(data.landmarks).length > 0) {
        const width = outputCanvas.width;
        const height = outputCanvas.height;
        const lms = data.landmarks;

        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 4;
        ctx.fillStyle = "#E30022";

        // Draw connecting lines
        data.connections.forEach(([startIdx, endIdx]) => {
            const start = lms[startIdx];
            const end = lms[endIdx];
            if (start && end) {
                ctx.beginPath();
                ctx.moveTo(start.x * width, start.y * height);
                ctx.lineTo(end.x * width, end.y * height);
                ctx.stroke();
            }
        });

        // Draw joint nodes
        Object.values(lms).forEach(lm => {
            if (lm) {
                ctx.beginPath();
                ctx.arc(lm.x * width, lm.y * height, 6, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    }

    // Request the next frame loop
    requestAnimationFrame(sendFrame);
};