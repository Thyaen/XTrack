const socket = io();
console.log("Socket.IO verbunden.");

const camCanvas = document.getElementById('camCanvas');
const camCtx = camCanvas.getContext('2d');
// Fixe Größe für Canvas
camCanvas.width = 640;
camCanvas.height = 480;


let latestFrame = null;

// Kamera-Stream → Frame speichern
socket.on('camera_frame', function(data) {
  if (!data.frame) return;
  latestFrame = new Image();
  latestFrame.src = 'data:image/jpeg;base64,' + data.frame;
});

// Zeichenschleife
function drawLoop() {
  if (latestFrame && latestFrame.complete) {
    camCtx.clearRect(0, 0, camCanvas.width, camCanvas.height);
    camCtx.drawImage(latestFrame, 0, 0, camCanvas.width, camCanvas.height);
  }
  requestAnimationFrame(drawLoop);
}

drawLoop();  // Start der Endlosschleife
