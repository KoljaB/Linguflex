var s, pw;

var xhr_1 = new XMLHttpRequest();
xhr_1.open("GET", "/credentials", false);
xhr_1.onreadystatechange = function() {
    if (xhr_1.readyState == 4 && xhr_1.status == 200) {
        var response = JSON.parse(xhr_1.responseText);
        s = response.host;
        pw = response.port;
    }
}
xhr_1.send();

let socket_adress = "wss://" + s + ":" + pw;
let socket = null;
let displayDiv = document.getElementById('textDisplay');
let server_available = false;
let mic_available = false;
let fullUserSentences = [];
let fullAssistantSentences = [];
let current_assistant_text = "";
let chunkCounter = 0;

const serverCheckInterval = 5000; 

let audioContext;

// Initialization of the connection state flag and button element
let shouldAttemptReconnect = true;
const connectButton = document.createElement('button');
document.body.appendChild(connectButton);
updateButton();

function getAudioContext() {
    if (!audioContext) {
        audioContext = new AudioContext();
        console.log('Sample rate:', audioContext.sampleRate);

        // Load the worklet processor
        audioContext.audioWorklet.addModule('/static/audio-processor.js').then(() => {
            console.log("AudioWorklet module loaded successfully");
        }).catch(e => {
            console.error("Error loading AudioWorklet module:", e);
        });
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    return audioContext;
}

document.addEventListener('click', () => {
    const audioCtx = getAudioContext();
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
});


async function streamAudio() {
    try {
        const audioCtx = getAudioContext();

        // Ensure the processorNode is created and connected only once
        if (!window.processorNode) {
            window.processorNode = new AudioWorkletNode(audioCtx, 'stream-audio-processor');
            window.processorNode.port.onmessage = (event) => {
                console.log(event.data);  // Log the message received from the worklet
            };
            window.processorNode.connect(audioCtx.destination);
        }

        const response = await fetch('/tts');
        if (!response.body) {
            throw new Error('ReadableStream not supported or no body in the response');
        }

        const reader = response.body.getReader();

        async function push() {
            const { done, value } = await reader.read();
            chunkCounter++;
            console.log("Chunk", chunkCounter);
            if (done) {
                console.log("Stream finished.");
                return;
            }
            // Post the audio data to the processor
            if (value instanceof Uint8Array) {
                window.processorNode.port.postMessage(value.buffer);
            } else {
                window.processorNode.port.postMessage(value);
            }
            push(); // Continue reading
        }

        push();
    } catch (err) {
        console.error('Failed to fetch audio:', err);
    }
}


async function speak() {
    const audioCtx = getAudioContext();
    if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
    }    
    const blob = await streamAudio();
    if (!blob) return;

    const arrayBuffer = await blob.arrayBuffer();
    audioCtx.decodeAudioData(arrayBuffer, buffer => {
        const sourceNode = audioCtx.createBufferSource();
        sourceNode.buffer = buffer;
        sourceNode.connect(audioCtx.destination);
        sourceNode.start();
    }, e => console.error('Error decoding audio data:', e));
}

function updateButton() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        connectButton.textContent = "Disconnect";
        connectButton.onclick = function() {
            disconnectFromServer();  
            // shouldAttemptReconnect = false;
            // socket.close();
        };
    } else {
        connectButton.textContent = "Connect";
        connectButton.onclick = function() {
            shouldAttemptReconnect = true;
            createSocket(socket_adress);
        };
    }
}

function createSocket(address) {
    // if (socket !== null && socket.readyState !== WebSocket.CLOSED) {
    //     socket.close();
    // }    
    if (socket) {
        shouldAttemptReconnect = false;
        socket.close();
    }

   // Clean up existing processorNode if it exists
    if (window.processorNode) {
        window.processorNode.disconnect();
        window.processorNode = null;
    }    
    socket = new WebSocket(address);
    socket.onopen = function(event) {
        server_available = true;
        updateButton();
        start_msg();
    };
    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        if (data.type === 'realtime_user') {
            if (current_assistant_text != "") {
                fullAssistantSentences.push(current_assistant_text);
                current_assistant_text = "";
            }
            displayRealtimeText(data.text, displayDiv, false);
        } else if (data.type === 'realtime_assistant') {
            current_assistant_text = data.text;
            displayRealtimeText(data.text, displayDiv, true);
        } else if (data.type === 'final_usertext') {
            fullUserSentences.push(data.text);
            displayRealtimeText("", displayDiv, false);
        } else if (data.type === 'audio_stream_ready') {
            chunkCounter = 0;
            speak();
        }
    };
    socket.onclose = function(event) {
        server_available = false;
        shouldAttemptReconnect = false;
        updateButton();
    };

    setupMicrophone();
}



function connectToServer() {
    createSocket(socket_adress);    
}

function disconnectFromServer() {
    fetch('/disconnect', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);  // Log the server response
            shouldAttemptReconnect = false;  // Prevent automatic reconnect
            if (socket) {
                socket.close();  // Close the WebSocket connection
            }
            updateButton();  // Update the connect/disconnect button
        })
        .catch(error => console.error('Error disconnecting:', error));
}

function displayRealtimeText(realtimeText, displayDiv, isAssistant = false) {
    let combinedSentences = [];
    let maxLength = Math.max(fullUserSentences.length, fullAssistantSentences.length);

    for (let i = 0; i < maxLength; i++) {
        if (i < fullUserSentences.length) {
            let userSpan = document.createElement('span');
            userSpan.textContent = fullUserSentences[i] + " ";
            userSpan.className = 'user_finaltext';
            combinedSentences.push(userSpan.outerHTML + "<br>");
        }
        if (i < fullAssistantSentences.length) {
            let assistantSpan = document.createElement('span');
            assistantSpan.textContent = fullAssistantSentences[i] + " ";
            assistantSpan.className = 'assistant_finaltext';
            combinedSentences.push(assistantSpan.outerHTML + "<br>");
        }
    }

    let fulltext = ""
    if (isAssistant) {
        let assistantSpan = document.createElement('span');
        assistantSpan.textContent = realtimeText + " ";
        assistantSpan.className = 'assistant_realtimetext';
        fulltext = combinedSentences.join('') + assistantSpan.outerHTML + "<br>";
    } else {
        let userSpan = document.createElement('span');
        userSpan.textContent = realtimeText + " ";
        userSpan.className = 'user_realtimetext';
        fulltext = combinedSentences.join('') + userSpan.outerHTML + "<br>";
    }

    displayDiv.innerHTML = fulltext;  // corrected variable name here from 'displayedText' to 'fulltext'
}

function start_msg() {
    if (!mic_available)
        displayRealtimeText("🎤  please allow microphone access  🎤", displayDiv);
    else if (!server_available)
        displayRealtimeText("🖥️  please start server  🖥️", displayDiv);
    else
        displayRealtimeText("👄  start speaking  👄", displayDiv);
};

// Check server availability periodically
setInterval(() => {
    if (!server_available && shouldAttemptReconnect) {
        connectToServer();
    }
}, serverCheckInterval);

async function setupMicrophone() {
    try {
        // Check if the browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Browser does not support getUserMedia!");
        }

        // Attempt to get the media stream
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = getAudioContext();
        
        // Ensure the audio context is in a valid state
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        await audioContext.audioWorklet.addModule('static/microphone-processor.js');

        const source = audioContext.createMediaStreamSource(stream);
        const processorNode = new AudioWorkletNode(audioContext, 'microphone-processor');

        processorNode.port.onmessage = event => {
            const channelData = event.data;
            sendAudioData(channelData);  // Function to handle data transmission
        };

        source.connect(processorNode);
        processorNode.connect(audioContext.destination);

        // Successful setup
        mic_available = true;
        start_msg();

    } catch (error) {
        console.error("Microphone setup failed:", error);
        mic_available = false;
        start_msg();
        // Provide user feedback about the error
        if (error.name === "NotAllowedError") {
            alert("Microphone access was denied. Please allow microphone access and try again.");
        } else if (error.name === "NotFoundError") {
            alert("No microphone devices found.");
        } else {
            alert("An error occurred: " + error.message);
        }
    }
}


// Function to handle WebSocket transmission
function sendAudioData(audioData) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const sampleRate = audioContext.sampleRate;
        const metadata = { sampleRate };
        const metadataStr = JSON.stringify(metadata);
        const metadataBytes = new TextEncoder().encode(metadataStr);
        const audioDataBuffer = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            audioDataBuffer[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
        }
        const metadataLength = new ArrayBuffer(4);
        const view = new DataView(metadataLength);
        view.setUint32(0, metadataBytes.length, true);
        const combinedData = new Blob([metadataLength, metadataBytes, audioDataBuffer.buffer]);
        socket.send(combinedData);
    }
}


start_msg()
connectToServer();
