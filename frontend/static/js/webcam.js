const video = document.querySelector('.tvc-wc-video video');
const outputCanvas = document.querySelector('.tvc-wc-video canvas');
const ctx = outputCanvas.getContext('2d');

const repsContainer = document.querySelector('.tvc-reps-counter-l');
const repsSpan = repsContainer.querySelector('p');

const repsContainer2 = document.querySelector('.tvc-reps-counter-r');
const repsSpan2 = repsContainer2 ? repsContainer2.querySelector('p') : null;

const hiddenCanvas = document.createElement('canvas');
hiddenCanvas.width = 1280;
hiddenCanvas.height = 720;
const hiddenCtx = hiddenCanvas.getContext('2d');

const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/video/${currentExerciseId}`);

ws.binaryType = "blob";

function sendFrame() {
    if (ws.readyState === WebSocket.OPEN && video.readyState === video.HAVE_ENOUGH_DATA) {
        hiddenCtx.drawImage(video, 0, 0, hiddenCanvas.width, hiddenCanvas.height);
        
        hiddenCanvas.toBlob((blob) => {
            if (blob) {
                ws.send(blob);
            }
        }, 'image/jpeg', 0.7);
    }
}

ws.onopen = () => {
    console.log("Verbunden. Starte Kamera...");
    
    navigator.mediaDevices.getUserMedia({ 
        video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 }
        } 
    })
    .then(stream => {
        video.srcObject = stream;

        video.setAttribute('playsinline', ''); 
        video.setAttribute('autoplay', '');
        video.setAttribute('muted', '');
        video.muted = true;
        
        video.onloadedmetadata = () => {
            const actualWidth = video.videoWidth;
            const actualHeight = video.videoHeight;
            
            outputCanvas.width = actualWidth;
            outputCanvas.height = actualHeight;
            
            hiddenCanvas.width = actualWidth;
            hiddenCanvas.height = actualHeight;

            video.play().catch(err => {
                console.error("Safari blocked video playback:", err);
            });
        };

        video.onplaying = () => {
            sendFrame();
        };
    })
    .catch(err => console.error("Kamera-Fehler:", err));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.stats && repsContainer && repsSpan) {

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

    ctx.drawImage(hiddenCanvas, 0, 0, outputCanvas.width, outputCanvas.height);

    if (Object.keys(data.landmarks).length > 0) {
        const width = outputCanvas.width;
        const height = outputCanvas.height;
        const lms = data.landmarks;

        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 4;
        ctx.fillStyle = "#B50019";

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

        Object.values(lms).forEach(lm => {
            if (lm) {
                ctx.beginPath();
                ctx.arc(lm.x * width, lm.y * height, 6, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    }

    requestAnimationFrame(() => {
        sendFrame();
    });
};