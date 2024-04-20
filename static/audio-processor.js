// RingBuffer class for managing audio data efficiently
class RingBuffer {
    constructor(size) {
        this.buffer = new Float32Array(size);
        this.readIndex = 0;
        this.writeIndex = 0;
        this.available = 0;
        this.size = size;
    }

    push(data) {
        data.forEach(sample => {
            if (this.available < this.size) { // Prevent overflow
                this.buffer[this.writeIndex] = sample;
                this.writeIndex = (this.writeIndex + 1) % this.size;
                this.available++;
            }
        });
    }

    pull(amount) {
        let output = new Float32Array(amount);
        for (let i = 0; i < amount; i++) {
            if (this.available > 0) { // Ensure data is available
                output[i] = this.buffer[this.readIndex];
                this.readIndex = (this.readIndex + 1) % this.size;
                this.available--;
            } else {
                output[i] = 0; // Output silence if buffer is empty
            }
        }
        return output;
    }
}

// StreamAudioProcessor using RingBuffer to manage audio samples
class StreamAudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.audioBuffer = new RingBuffer(60 * 48000); // Buffer size of 1 second at 48 kHz
        this.started = false; // Flag to control the start of processing
        this.minimumThreshold = 24000; // Start processing after half a second of audio is buffered

        this.port.onmessage = (event) => {
            try {
                if (event.data instanceof ArrayBuffer) {
                    const incomingData = new DataView(event.data);
                    const numFloats = incomingData.byteLength / 4;
                    const audioData = new Float32Array(numFloats);

                    for (let i = 0; i < numFloats; i++) {
                        audioData[i] = incomingData.getFloat32(i * 4, true);
                    }
                    this.audioBuffer.push(audioData); // Push array to the ring buffer
                    if (!this.started && this.audioBuffer.available >= this.minimumThreshold) {
                        this.started = true; // Start processing when threshold is reached
                    }
                }
            } catch (error) {
                console.error(`Error processing data: ${error.message}`);
            }
        };
    }

    process(inputs, outputs, parameters) {
        const output = outputs[0];
        for (let channel = 0; channel < output.length; channel++) {
            const outputChannel = output[channel];
            if (this.started) {
                const samplesToProcess = this.audioBuffer.pull(outputChannel.length);
                outputChannel.set(samplesToProcess);
            } else {
                outputChannel.fill(0); // Fill with silence if not started
            }
        }
        return true; // Keep the processor alive
    }
}

registerProcessor('stream-audio-processor', StreamAudioProcessor);

