// microphone-processor.js
class MicrophoneProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        const output = input; // Assuming pass-through, modify as needed

        if (input.length > 0) {
            const channelData = input[0]; // Assuming mono input
            this.port.postMessage(channelData);
        }

        return true; // Keep processor running
    }
}

registerProcessor('microphone-processor', MicrophoneProcessor);




// // microphone-processor.js
// class MicrophoneProcessor extends AudioWorkletProcessor {
//     constructor() {
//         super();
//         this.port.onmessage = (event) => {
//             // Messages from the main thread could include commands or WebSocket details
//             this.socket = event.data.socket;
//         };
//     }

//     process(inputs) {
//         const input = inputs[0];
//         const output = input; // Assuming pass-through, modify as needed for your application

//         if (this.socket && this.socket.readyState === WebSocket.OPEN) {
//             const channelData = input[0]; // Assuming mono input for simplicity
//             const sampleRate = sampleRate;
//             const metadata = { sampleRate };
//             const metadataStr = JSON.stringify(metadata);
//             const metadataBytes = new TextEncoder().encode(metadataStr);
//             const audioData = new Int16Array(channelData.length);
//             for (let i = 0; i < channelData.length; i++) {
//                 audioData[i] = Math.max(-32768, Math.min(32767, channelData[i] * 32768));
//             }
//             const metadataLength = new ArrayBuffer(4);
//             const view = new DataView(metadataLength);
//             view.setUint32(0, metadataBytes.length, true);
//             this.socket.send(new Blob([metadataLength, metadataBytes, audioData.buffer]));
//         }

//         return true; // Keep processor running
//     }
// }

// registerProcessor('microphone-processor', MicrophoneProcessor);
