// Voice AI Web App
const CONFIG = {
    wsUrl: 'wss://voice-ai-server-5v7k.onrender.com',
    autoPlay: true
};

let ws = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

const pttButton = document.getElementById('pttButton');
const status = document.getElementById('status');
const conversation = document.getElementById('conversation');

// Connect to WebSocket
function connect() {
    status.textContent = 'Connecting...';
    
    ws = new WebSocket(CONFIG.wsUrl);
    
    ws.onopen = () => {
        status.textContent = 'Connected! Hold button to speak';
        console.log('Connected to server');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
    
    ws.onerror = (error) => {
        status.textContent = 'Error connecting. Retrying...';
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        status.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connect, 3000);
    };
}

// Handle incoming messages
function handleMessage(data) {
    if (data.type === 'transcription') {
        addMessage('You: ' + data.text, 'user');
    } else if (data.type === 'response') {
        addMessage('AI: ' + data.text, 'ai');
        if (data.audio) {
            playAudio(data.audio);
        }
    } else if (data.type === 'error') {
        status.textContent = 'Error: ' + data.message;
    }
}

// Add message to conversation
function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = 'message ' + sender;
    div.textContent = text;
    conversation.appendChild(div);
    conversation.scrollTop = conversation.scrollHeight;
}

// Play audio from base64
function playAudio(base64Audio) {
    const audio = new Audio('data:audio/mp3;base64,' + base64Audio);
    audio.play();
}

// Start recording
async function startRecording() {
    if (isRecording) return;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudio(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        isRecording = true;
        pttButton.classList.add('recording');
        status.textContent = 'Recording...';
        
    } catch (err) {
        status.textContent = 'Microphone access denied';
        console.error('Error:', err);
    }
}

// Stop recording
function stopRecording() {
    if (!isRecording) return;
    
    mediaRecorder.stop();
    isRecording = false;
    pttButton.classList.remove('recording');
    status.textContent = 'Processing...';
}

// Send audio to server
function sendAudio(audioBlob) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        status.textContent = 'Not connected';
        return;
    }
    
    const reader = new FileReader();
    reader.onloadend = () => {
        const base64Audio = reader.result.split(',')[1];
        ws.send(JSON.stringify({
            type: 'audio',
            data: base64Audio
        }));
    };
    reader.readAsDataURL(audioBlob);
}

// Event listeners
pttButton.addEventListener('mousedown', startRecording);
pttButton.addEventListener('mouseup', stopRecording);
pttButton.addEventListener('mouseleave', stopRecording);

pttButton.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startRecording();
});
pttButton.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopRecording();
});

// Initialize
connect();
