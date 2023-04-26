let video = $('#video')[0];
let canvas = $('#canvas')[0];
let ctx = canvas.getContext('2d');
let output = $('#output')[0];
const extractedTextElement = $('#extracted-text')[0];
const cameraSelect = $('#camera-select')[0];
let currentStream = null;
let reconnectAttempts = 0;
let skippedFrames = 0;
let framesPerSecond = 1;

function stopStream(stream) {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

function switchCamera(deviceId) {
    if (currentStream) {
        stopStream(currentStream);
    }

    navigator.mediaDevices.getUserMedia({
        video: {
            deviceId: deviceId,
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }, audio: false
    })
        .then(stream => {
            currentStream = stream;
            video.srcObject = stream;
            video.play();
        })
        .catch(err => {
            console.error("An error occurred: " + err);
        });
}


navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        const cameras = devices.filter(device => device.kind === 'videoinput');
        cameras.forEach(camera => {
            const option = $('<option></option>');
            option.val(camera.deviceId);
            option.text(camera.label || `Camera ${cameras.indexOf(camera) + 1}`);
            $('#camera-select').append(option);
        });
        // Set up event listener for camera selection
        $('#camera-select').on('change', () => {
            switchCamera(cameraSelect.value);
            localStorage.setItem('selectedCamera', cameraSelect.value);
        });

        // Read the values from localStorage
        const savedCamera = localStorage.getItem('selectedCamera');
        const savedRotation = localStorage.getItem('selectedRotation');

        // Start with the saved camera or the first camera
        if (cameras.length > 0) {
            switchCamera(savedCamera || cameras[0].deviceId);
        }

        // Set the saved rotation or the default rotation
        $('#rotation-select').val(savedRotation || "0");
        applyRotation(); // Apply the initial rotation
    });

function reconnectOnDisconnect(socket) {
    if (reconnectAttempts < 60) {
        reconnectAttempts++;
        console.log('WebSocket connection closed. Attempting to reconnect...');
        setTimeout(() => {
            console.log(`${reconnectAttempts} attempts remaining`);
            const newSocket = connectWebSocket(reconnectAttempts - 1);
            if (newSocket !== null) {
                socket = newSocket;
            }
        }, 5000);
    } else {
        console.log('Maximum number of WebSocket reconnection attempts reached.');
    }
}

function connectWebSocket(reconnectAttempts = 10) {
    if (reconnectAttempts <= 0) {
        console.error('Maximum number of WebSocket reconnection attempts reached.');
    }
    let socket = new WebSocket('wss://' + window.location.host + '/ws/serial_camera/');

    socket.onopen = function (event) {
        console.log('WebSocket connection opened:', event);
        reconnectAttempts = 0;
        skippedFrames = 0;
    };

    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
        reconnectOnDisconnect(socket);
    };

    socket.onclose = function (event) {
        console.log('WebSocket connection closed:', event);
        // Reconnect after a delay
        reconnectOnDisconnect(socket);
    };



    socket.onmessage = function (event) {
        const data = event.data;
        if (data.startsWith('image_stream: ')) {
            // Update the image source with the received base64 data
            let img_data = 'data:image/png;base64,' + event.data;
            output.src = img_data.replace('image_stream: ', '');
        } else {
            // Update the extracted text
            extractedTextElement.innerText = 'Extracted text: ' + data.replace('text_stream: ', '');
        }
    };

    return socket;
}

let socket = connectWebSocket();


const rotationSelect = $('#rotation-select')[0];

function applyRotation() {
    const rotation = rotationSelect.value;
    // Apply the rotation to both video and output image elements
    video.style.transform = `rotate(${rotation}deg)`;
};

$('#rotation-select').on('change', () => {
    applyRotation();
    localStorage.setItem('selectedRotation', rotationSelect.value);
});

function sendFrame(processFrameBool = false) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const rotation = parseFloat(rotationSelect.value);
        const radians = (Math.PI / 180) * rotation;
        const swapDimensions = rotation % 180 !== 0;

        canvas.width = swapDimensions ? video.videoHeight : video.videoWidth;
        canvas.height = swapDimensions ? video.videoWidth : video.videoHeight;

        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(radians);
        ctx.drawImage(video, -video.videoWidth / 2, -video.videoHeight / 2, video.videoWidth, video.videoHeight);
        ctx.restore();

        const base64Image = canvas.toDataURL('image/png').split(',')[1];
        const frameData = {
            timestamp: new Date().toISOString(),
            image: base64Image,
            process: processFrameBool
        };
        socket.send(JSON.stringify(frameData));
    } else {
        console.warn('WebSocket connection is not open. Skipping frame send.');
        skippedFrames++;
        if (skippedFrames > 10) {
            console.warn('Too many skipped frames. Attempting to reconnect...');
            socket = connectWebSocket(socket);
            skippedFrames = 0;
        }
        //reconnectOnDisconnect(socket, reconnectAttempts);
    }
}

setInterval(sendFrame, 1000 / framesPerSecond);  // Send frames at 10 FPS

function sendTenFrames() {
    let frameCount = 0;
    const frameInterval = 1000 / 30; // 30 FPS

    const sendFrameInterval = setInterval(() => {
        frameCount++;
        sendFrame(true);


        if (frameCount >= 10) {
            clearInterval(sendFrameInterval);
        }
    }, frameInterval);
}
const sendTenFramesBtn = $('#send-ten-frames-btn')[0];
$(sendTenFramesBtn).on('click', sendTenFrames);