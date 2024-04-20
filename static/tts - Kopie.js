let socket_adress = "wss://192.168.178.22:8001";
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


// async function streamAudio() {
//     try {
//         const audioCtx = getAudioContext();

//         const response = await fetch('/tts');
//         if (!response.body) {
//             throw new Error('ReadableStream not supported or no body in the response');
//         }

//         const reader = response.body.getReader();
//         const processorNode = new AudioWorkletNode(audioCtx, 'stream-audio-processor');
//         processorNode.port.onmessage = (event) => {
//             console.log(event.data);  // Log the message received from the worklet
//         };
//         processorNode.port.postMessage('Test message');
//         processorNode.connect(audioCtx.destination);

//         async function push() {
//             try {
//                 const { done, value } = await reader.read();
//                 chunkCounter++;
//                 console.log("Chunk", chunkCounter);
//                 if (done) {
//                     console.log("Stream finished.");
//                     processorNode.disconnect();
//                     return;
//                 }
//                 // Ensure the value is an ArrayBuffer before posting it
//                 if (value instanceof Uint8Array) {
//                     // Convert Uint8Array to ArrayBuffer if necessary
//                     processorNode.port.postMessage(value.buffer);
//                 } else {
//                     processorNode.port.postMessage(value);
//                 }                
//                 // if (processorNode.port) {
//                 //     processorNode.port.postMessage(value);
//                 // }
//                 push(); // Keep reading
//             } catch (readError) {
//                 console.error("Stream reading failed:", readError);
//                 processorNode.disconnect();
//             }
//         }

//         push();
//     } catch (err) {
//         console.error('Failed to fetch audio:', err);
//     }
// }

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

function createSocket(address) {
    socket = new WebSocket(address);
    socket.onopen = function(event) {
        server_available = true;
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
            displayRealtimeText("", displayDiv, false); // Refresh display with new full sentence
        } else if (data.type === 'audio_stream_ready') {
            chunkCounter = 0;
            speak();
        }
    };
    socket.onclose = function(event) {
        server_available = false;
    };

    setupMicrophone();
}



function connectToServer() {
    createSocket(socket_adress);    
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
    if (!server_available) {
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


















// let socket_adress = "wss://192.168.178.22:8001";
// let socket = null;
// let displayDiv = document.getElementById('textDisplay');
// let server_available = false;
// let mic_available = false;
// let fullUserSentences = [];
// let fullAssistantSentences = [];
// let current_assistant_text = "";
// let chunkCounter = 0;
// const serverCheckInterval = 5000; 
// let audioContext;
// let audioBuffer;
// let playStarted = false;
// // let nextPlayTime = 0;

// function getAudioContext() {
//     if (!audioContext) {
//         audioContext = new AudioContext();
//         console.log('Sample rate:', audioContext.sampleRate);
//     }
//     if (audioContext.state === 'suspended') {
//         audioContext.resume();
//     }
//     return audioContext;
// }

// document.addEventListener('click', () => {
//     const audioCtx = getAudioContext();
//     if (audioCtx.state === 'suspended') {
//         audioCtx.resume();
//     }
// });

// // async function streamAudio() {
// //     try {
// //         const audioCtx = getAudioContext();
// //         const response = await fetch('/tts');
// //         if (!response.body) {
// //             throw new Error('ReadableStream not supported or no body in the response');
// //         }
// //         const reader = response.body.getReader();

// //         async function readAndPlay() {
// //             const { done, value } = await reader.read();
// //             if (done) {
// //                 console.log("Stream finished.");
// //                 return;
// //             }
// //             chunkCounter++;
// //             console.log("Chunk", chunkCounter);

// //             // Create buffer from the chunk
// //             audioCtx.decodeAudioData(value.buffer, function(buffer) {
// //                 playAudio(buffer);
// //             }, function(e) {
// //                 console.log("Error with decoding audio data" + e.err);
// //             });

// //             readAndPlay(); // Continue reading and playing next chunks
// //         }

// //         readAndPlay();
// //     } catch (err) {
// //         console.error('Failed to fetch audio:', err);
// //     }
// // }

// // function playAudio(buffer) {
// //     const audioCtx = getAudioContext();
// //     const sourceNode = audioCtx.createBufferSource();
// //     sourceNode.buffer = buffer;
// //     sourceNode.connect(audioCtx.destination);
// //     if (nextPlayTime < audioCtx.currentTime) {
// //         // If buffer underrun, play as soon as possible.
// //         nextPlayTime = audioCtx.currentTime;
// //     }
// //     sourceNode.start(nextPlayTime);
// //     // Schedule next play time
// //     nextPlayTime += buffer.duration;
// // }

// async function streamAudio() {
//     try {
//         const audioCtx = getAudioContext();
//         const response = await fetch('/tts');
//         if (!response.body) {
//             throw new Error('ReadableStream not supported or no body in the response');
//         }
//         const reader = response.body.getReader();
//         audioBuffer = audioCtx.createBuffer(1, audioCtx.sampleRate * 60 * 10, audioCtx.sampleRate);
//         let audioData = audioBuffer.getChannelData(0);
//         let currentOffset = 0;

//         async function push() {
//             try {
//                 const { done, value } = await reader.read();
//                 chunkCounter++;
//                 console.log("Chunk", chunkCounter);
//                 if (playStarted == false && (done || chunkCounter > 20)) {
//                     playStarted = true;
//                     console.log("Stream finished.");
//                     playAudio();
//                     return;
//                 }

//                 // Ensure the byte length is a multiple of 4
//                 let byteLength = value.byteLength;
//                 let adjustedLength = byteLength - (byteLength % 4);
//                 const float32Array = new Float32Array(value.buffer.slice(0, adjustedLength));

//                 audioData.set(float32Array, currentOffset);
//                 currentOffset += float32Array.length;
//                 push(); // Keep reading 
//             } catch (readError) {
//                 console.error("Stream reading failed:", readError);
//             }
//         }
//         push();
//     } catch (err) {
//         console.error('Failed to fetch audio:', err);
//     }
// }

// function playAudio() {
//     const audioCtx = getAudioContext();
//     const sourceNode = audioCtx.createBufferSource();
//     sourceNode.buffer = audioBuffer;
//     sourceNode.connect(audioCtx.destination);
//     sourceNode.start();

//     // Reset the audio buffer and chunk counter for the next synthesis
//     audioBuffer = null;
//     chunkCounter = 0;    
// }

// function createSocket(address) {
//     socket = new WebSocket(address);
//     socket.onopen = function(event) {
//         server_available = true;
//         start_msg();
//     };
//     socket.onmessage = function(event) {
//         let data = JSON.parse(event.data);
//         if (data.type === 'realtime_user') {
//             if (current_assistant_text != "") {
//                 fullAssistantSentences.push(current_assistant_text);
//                 current_assistant_text = "";
//             }
//             displayRealtimeText(data.text, displayDiv, false);
//         } else if (data.type === 'realtime_assistant') {
//             current_assistant_text = data.text;
//             displayRealtimeText(data.text, displayDiv, true);
//         } else if (data.type === 'final_usertext') {
//             fullUserSentences.push(data.text);
//             displayRealtimeText("", displayDiv, false); // Refresh display with new full sentence
//         } else if (data.type === 'audio_stream_ready') {
//             playStarted = false;
//             chunkCounter = 0;
//             streamAudio();
//         }
//     };
//     socket.onclose = function(event) {
//         server_available = false;
//     };
//     setupMicrophone();
// }

// function connectToServer() {
//     createSocket(socket_adress);    
// }

// function displayRealtimeText(realtimeText, displayDiv, isAssistant = false) {
//     let combinedSentences = [];
//     let maxLength = Math.max(fullUserSentences.length, fullAssistantSentences.length);
//     for (let i = 0; i < maxLength; i++) {
//         if (i < fullUserSentences.length) {
//             let userSpan = document.createElement('span');
//             userSpan.textContent = fullUserSentences[i] + " ";
//             userSpan.className = 'user_finaltext';
//             combinedSentences.push(userSpan.outerHTML);
//         }
//         if (i < fullAssistantSentences.length) {
//             let assistantSpan = document.createElement('span');
//             assistantSpan.textContent = fullAssistantSentences[i] + " ";
//             assistantSpan.className = 'assistant_finaltext';
//             combinedSentences.push(assistantSpan.outerHTML);
//         }
//     }
//     let fulltext = ""
//     if (isAssistant) {
//         let assistantSpan = document.createElement('span');
//         assistantSpan.textContent = realtimeText + " ";
//         assistantSpan.className = 'assistant_realtimetext';
//         fulltext = combinedSentences.join('') + assistantSpan.outerHTML;
//     } else {
//         let userSpan = document.createElement('span');
//         userSpan.textContent = realtimeText + " ";
//         userSpan.className = 'user_realtimetext';
//         fulltext = combinedSentences.join('') + userSpan.outerHTML;
//     }
//     displayDiv.innerHTML = fulltext;
// }

// function start_msg() {
//     if (!mic_available)
//         displayRealtimeText("🎤  please allow microphone access  🎤", displayDiv);
//     else if (!server_available)
//         displayRealtimeText("🖥️  please start server  🖥️", displayDiv);
//     else
//         displayRealtimeText("👄  start speaking  👄", displayDiv);
// };

// // Check server availability periodically
// setInterval(() => {
//     if (!server_available) {
//         connectToServer();
//     }
// }, serverCheckInterval);

// async function setupMicrophone() {
//     try {
//         // Check if the browser supports getUserMedia
//         if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
//             throw new Error("Browser does not support getUserMedia!");
//         }
//         // Attempt to get the media stream
//         const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//         const audioContext = getAudioContext();
        
//         // Ensure the audio context is in a valid state
//         if (audioContext.state === 'suspended') {
//             await audioContext.resume();
//         }
//         await audioContext.audioWorklet.addModule('static/microphone-processor.js');
//         const source = audioContext.createMediaStreamSource(stream);
//         const processorNode = new AudioWorkletNode(audioContext, 'microphone-processor');
//         processorNode.port.onmessage = event => {
//             const channelData = event.data;
//             sendAudioData(channelData);  // Function to handle data transmission
//         };
//         source.connect(processorNode);
//         processorNode.connect(audioContext.destination);
//         // Successful setup
//         mic_available = true;
//         start_msg();
//     } catch (error) {
//         console.error("Microphone setup failed:", error);
//         mic_available = false;
//         start_msg();
//         // Provide user feedback about the error
//         if (error.name === "NotAllowedError") {
//             alert("Microphone access was denied. Please allow microphone access and try again.");
//         } else if (error.name === "NotFoundError") {
//             alert("No microphone devices found.");
//         } else {
//             alert("An error occurred: " + error.message);
//         }
//     }
// }

// // Function to handle WebSocket transmission
// function sendAudioData(audioData) {
//     if (socket && socket.readyState === WebSocket.OPEN) {
//         const sampleRate = audioContext.sampleRate;
//         const metadata = { sampleRate };
//         const metadataStr = JSON.stringify(metadata);
//         const metadataBytes = new TextEncoder().encode(metadataStr);
//         const audioDataBuffer = new Int16Array(audioData.length);
//         for (let i = 0; i < audioData.length; i++) {
//             audioDataBuffer[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
//         }
//         const metadataLength = new ArrayBuffer(4);
//         const view = new DataView(metadataLength);
//         view.setUint32(0, metadataBytes.length, true);
//         const combinedData = new Blob([metadataLength, metadataBytes, audioDataBuffer.buffer]);
//         socket.send(combinedData);
//     }
// }

// start_msg()
// connectToServer();