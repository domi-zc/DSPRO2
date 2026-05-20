const video = document.querySelector('.tvc-camera-container-video video');
const outputCanvas = document.querySelector('.tvc-camera-container-video canvas');
const ctx = outputCanvas.getContext('2d');

const repsContainer = document.querySelector('.tvc-reps-counter-l');
const repsSpan = repsContainer.querySelector('p');
const repsContainer2 = document.querySelector('.tvc-reps-counter-r');
const repsSpan2 = repsContainer2 ? repsContainer2.querySelector('p') : null;

// Hidden canvas for capturing frame blobs to send to the backend
const hiddenCanvas = document.createElement('canvas');
hiddenCanvas.width = 1280;
hiddenCanvas.height = 720;
const hiddenCtx = hiddenCanvas.getContext('2d');

// WebSocket & Camera Configuration
const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/exercise/${currentExerciseId}`);
ws.binaryType = "blob";

/**
 * Captures the current video frame, draws it to the hidden canvas, 
 * compresses it to JPEG, and sends it to the backend via WebSockets.
 */
function sendFrame() {
    if (ws.readyState === WebSocket.OPEN && video.readyState === video.HAVE_ENOUGH_DATA) {
        hiddenCtx.drawImage(video, 0, 0, hiddenCanvas.width, hiddenCanvas.height);
        
        hiddenCanvas.toBlob((blob) => {
            if (blob) ws.send(blob);
        }, 'image/jpeg', 0.7);
    }
}

ws.onopen = () => {
    console.log("Connected. Initializing camera...");
    
    navigator.mediaDevices.getUserMedia({ 
        video: { width: { ideal: 1280 }, height: { ideal: 720 } } 
    })
    .then(stream => {
        video.srcObject = stream;
        video.setAttribute('playsinline', ''); 
        video.setAttribute('autoplay', '');
        video.setAttribute('muted', '');
        video.muted = true;
        
        video.onloadedmetadata = () => {
            outputCanvas.width = video.videoWidth;
            outputCanvas.height = video.videoHeight;
            hiddenCanvas.width = video.videoWidth;
            hiddenCanvas.height = video.videoHeight;

            video.play().catch(err => console.error("Safari blocked video playback:", err));
        };

        video.onplaying = sendFrame;
    })
    .catch(err => console.error("Camera access error:", err));
};

// UI Updates & Pose Rendering
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Update Live Reps and State UI
    if (data.stats && repsContainer && repsSpan) {
        
        // Standard single-counter exercises
        if (data.stats["Reps"] !== undefined) {
            if (repsContainer2) repsContainer2.style.display = 'none';

            repsSpan.innerText = data.stats["Reps"];

            const displayState = data.stats["State"]; 
            if (displayState) {
                repsContainer.classList.remove('tvc-up', 'tvc-down');
                const stateLower = displayState.toLowerCase();
                if (stateLower === 'up') repsContainer.classList.add('tvc-up');
                else if (stateLower === 'down') repsContainer.classList.add('tvc-down');
            }

        // Dual-counter exercises (e.g., individual arms/legs)
        } else if (data.stats["Reps (Rechts)"] !== undefined) {
            if (repsContainer2) repsContainer2.style.display = '';

            repsSpan.innerText = "L" + data.stats["Reps (Links)"];
            if (repsSpan2) repsSpan2.innerText = "R" + data.stats["Reps (Rechts)"];

            const stateLeft = data.stats["State (Links)"];
            if (stateLeft) {
                repsContainer.classList.remove('tvc-up', 'tvc-down');
                const stateLowerLeft = stateLeft.toLowerCase();
                if (stateLowerLeft === 'up') repsContainer.classList.add('tvc-up');
                else if (stateLowerLeft === 'down') repsContainer.classList.add('tvc-down');
            }

            const stateRight = data.stats["State (Rechts)"];
            if (stateRight && repsContainer2) {
                repsContainer2.classList.remove('tvc-up', 'tvc-down');
                const stateLowerRight = stateRight.toLowerCase();
                if (stateLowerRight === 'up') repsContainer2.classList.add('tvc-up');
                else if (stateLowerRight === 'down') repsContainer2.classList.add('tvc-down');
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
        ctx.fillStyle = "#B50019";

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