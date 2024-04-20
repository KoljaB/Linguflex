import numpy as np
import resampy
from scipy.signal.windows import hann

class Resampler:
    """
    A class for resampling audio data from one sample rate to another, implementing the overlap-add method.
    Handles dynamic chunk sizes and different data types for input and output.
    """
    def __init__(self, input_sample_rate, output_sample_rate, overlap=0.5, dtype_in=np.int16, dtype_out=np.float32):
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.overlap = overlap  # Overlap as a fraction of the chunk size
        self.dtype_in = dtype_in
        self.dtype_out = dtype_out
        self.buffer = np.array([], dtype=self.dtype_out)  # Use dtype_out for processing buffer
        self.original_rate = input_sample_rate
        self.target_rate = output_sample_rate
        self.previous_chunk = None  # Stores the previous chunk for overlap
        self.resampled_previous_chunk = None  # Stores the resampled previous chunk

    def set_sample_rate(self, input_sample_rate, output_sample_rate):
        """Sets the input and output sample rates for the resampler."""
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate

    def resample(self, data):
        print("Resampling with overlap add")
        if self.previous_chunk is None:
            # For the first chunk, there's no previous data to overlap with
            processed_data = resampy.resample(data, self.original_rate, self.target_rate)
            half_index = len(processed_data) // 2
            self.previous_chunk = data
            self.resampled_previous_chunk = processed_data  # Store resampled data
            return processed_data[:half_index]
        else:
            # Combine previous chunk with current data
            combined_data = np.concatenate((self.previous_chunk, data))
            processed_data = resampy.resample(combined_data, self.original_rate, self.target_rate)

            # Retrieve the resampled length of the previous chunk
            resampled_prev_len = len(self.resampled_previous_chunk)
            half_index_prev = resampled_prev_len // 2
            half_index_current = (len(processed_data) - resampled_prev_len) // 2 + resampled_prev_len

            # Update previous chunk and its resampled version
            self.previous_chunk = data
            self.resampled_previous_chunk = resampy.resample(data, self.original_rate, self.target_rate)

            # Return the overlapping part of the resampled data
            return processed_data[half_index_prev:half_index_current]

    def flush(self):
        # Handle the last chunk of data
        if self.previous_chunk is not None:
            processed_data = self.resampled_previous_chunk
            half_index = len(processed_data) // 2
            self.previous_chunk = None
            self.resampled_previous_chunk = None
            return processed_data[half_index:]
        return np.array([], dtype=np.int16)

    def resample_plain(self, chunk: bytes) -> bytes:
        audio_array = np.frombuffer(chunk, dtype=self.dtype_in)
        # if self.dtype_in == np.int16:
        #     audio_array = audio_array.astype(self.dtype_out) / 32768.0  # Normalize int16 to float range -1.0 to 1.0
        #resampled_buffer = resampy.resample(audio_array, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
        resampled_buffer = resampy.resample(audio_array, self.input_sample_rate, self.output_sample_rate)
        # if self.dtype_out == np.float32:
        #     resampled_buffer = (resampled_buffer * 32768).astype(np.int16)  # Convert back to int16 if output is int16
        return resampled_buffer

    # def resample_plain(self, chunk: bytes) -> bytes:
    #     """Resamples an audio chunk without overlap."""
    #     audio_array = np.frombuffer(chunk, dtype=self.dtype_in)
    #     resampled_buffer = resampy.resample(audio_array.astype(self.dtype_out), self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
    #     return resampled_buffer.astype(self.dtype_out).tobytes()

    def resample_overlap_add(self, chunk: bytes) -> bytes:
        """Resamples an audio chunk using the overlap-add method."""
        audio_array = np.frombuffer(chunk, dtype=self.dtype_in).astype(self.dtype_out)
        chunk_size = audio_array.size
        overlap_size = int(chunk_size * self.overlap)

        window = hann(chunk_size, sym=False)
        windowed_audio = audio_array * window

        if self.buffer.size > 0:
            self.buffer = np.concatenate([self.buffer, np.zeros(overlap_size, dtype=self.dtype_out)])  # Extend buffer to fit the overlap
            self.buffer[-overlap_size * 2: -overlap_size] += windowed_audio[:overlap_size]
        self.buffer = np.concatenate([self.buffer, windowed_audio[overlap_size:]])

        resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
        resampled_output_size = int(chunk_size * self.output_sample_rate / self.input_sample_rate)
        output = resampled_buffer[:resampled_output_size].astype(self.dtype_out).tobytes()
        self.buffer = resampled_buffer[resampled_output_size:]

        return output

    # def flush(self) -> bytes:
    #     """Flushes the remaining buffer."""
    #     if self.buffer.size > 0:
    #         resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
    #         self.buffer = np.array([], dtype=self.dtype_out)
    #         return resampled_buffer.astype(self.dtype_out).tobytes()
    #     return b''



# import numpy as np
# import resampy
# from scipy.signal.windows import hann

# class Resampler:
#     """
#     A class for resampling audio data from one sample rate to another, implementing the overlap-add method.
#     Handles dynamic chunk sizes.
#     """
#     def __init__(self, input_sample_rate, output_sample_rate, overlap=0.5, dtype=np.int16):
#         self.input_sample_rate = input_sample_rate
#         self.output_sample_rate = output_sample_rate
#         self.overlap = overlap  # Overlap as a fraction of the chunk size
#         self.dtype = dtype
#         self.buffer = np.array([], dtype=self.dtype)

#     def set_sample_rate(self, input_sample_rate, output_sample_rate):
#         """Sets the input and output sample rates for the resampler.

#         Args:
#             input_sample_rate (int): The input sample rate.
#             output_sample_rate (int): The output sample rate.
#         """
#         self.input_sample_rate = input_sample_rate
#         self.output_sample_rate = output_sample_rate

#     def resample_plain(self, chunk: bytes) -> bytes:
#         audio_array = np.frombuffer(chunk, dtype=self.dtype)
#         resampled_buffer = resampy.resample(audio_array, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
#         return resampled_buffer

#     def resample_overlap_add(self, chunk: bytes) -> bytes:
#         audio_array = np.frombuffer(chunk, dtype=self.dtype)
#         chunk_size = audio_array.size
#         overlap_size = int(chunk_size * self.overlap)

#         # Create a window based on the current chunk size
#         window = hann(chunk_size, sym=False)

#         # Apply the window to the audio chunk
#         windowed_audio = audio_array * window

#         # Concatenate the new windowed audio to the buffer
#         if self.buffer.size > 0:
#             self.buffer = np.concatenate([self.buffer, np.zeros(overlap_size, dtype=self.dtype)])  # Extend the buffer at the end to fit the overlap
#             self.buffer[-overlap_size * 2: -overlap_size] += windowed_audio[:overlap_size]  # Add overlap
#         self.buffer = np.concatenate([self.buffer, windowed_audio[overlap_size:]])

#         # Resample the buffered audio
#         resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')

#         # Determine the size of resampled output to match the original audio chunk's duration
#         resampled_output_size = int(chunk_size * self.output_sample_rate / self.input_sample_rate)

#         # Prepare the output and adjust the buffer
#         output = resampled_buffer[:resampled_output_size].astype(self.dtype).tobytes()
#         self.buffer = resampled_buffer[resampled_output_size:]

#         return output

    # def resample_overlap_add(self, chunk: bytes) -> bytes:
    #     """Submits a chunk to the resampler, processes it, and handles overlap-add.
    #     Args:
    #         chunk (bytes): A chunk of audio data.
    #     Returns:
    #         bytes: The resampled chunk as bytes.
    #     """
    #     # Convert bytes to numpy array
    #     audio_array = np.frombuffer(chunk, dtype=self.dtype)
    #     chunk_size = audio_array.size
    #     overlap_size = int(chunk_size * self.overlap)

    #     # Create a dynamic window based on the current chunk size
    #     window = hann(chunk_size, sym=False)

    #     # Apply window function to the audio chunk
    #     windowed_audio = audio_array * window

    #     # Resample the windowed audio
    #     resampled_audio = resampy.resample(windowed_audio, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')

    #     # Calculate the resampled overlap size
    #     overlap_size_resampled = int(overlap_size * self.output_sample_rate / self.input_sample_rate)

    #     # Overlap-add process
    #     if self.buffer.size == 0:
    #         self.buffer = resampled_audio[:overlap_size_resampled]
    #         output_audio = resampled_audio[overlap_size_resampled:]
    #     else:
    #         # Ensure the buffer and the resampled audio have the same shape
    #         if self.buffer.size < overlap_size_resampled:
    #             self.buffer = np.pad(self.buffer, (0, overlap_size_resampled - self.buffer.size), mode='constant')
    #         elif self.buffer.size > overlap_size_resampled:
    #             self.buffer = self.buffer[-overlap_size_resampled:]

    #         # Overlap-add the resampled audio with the buffer
    #         output_audio = self.buffer + resampled_audio[:overlap_size_resampled]
    #         self.buffer = resampled_audio[overlap_size_resampled:2*overlap_size_resampled]
    #         output_audio = np.concatenate([output_audio, resampled_audio[2*overlap_size_resampled:]])

    #     # Convert numpy array back to bytes and return the resampled audio
    #     return output_audio
    
    # def resample_overlap_add(self, chunk: bytes) -> bytes:
    #     """Submits a chunk to the resampler, processes it, and handles overlap-add.
    #     Args:
    #         chunk (bytes): A chunk of audio data.
    #     Returns:
    #         bytes: The resampled chunk as bytes.
    #     """
    #     # Convert bytes to numpy array
    #     audio_array = np.frombuffer(chunk, dtype=self.dtype)
    #     chunk_size = audio_array.size
    #     overlap_size = int(chunk_size * self.overlap)

    #     # Create a dynamic window based on the current chunk size
    #     window = hann(chunk_size, sym=False)

    #     # Apply window function to the audio chunk
    #     windowed_audio = audio_array * window

    #     # Resample the windowed audio
    #     resampled_audio = resampy.resample(windowed_audio, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')

    #     # Overlap-add process
    #     if self.buffer.size == 0:
    #         self.buffer = resampled_audio
    #     else:
    #         # Ensure the buffer has the correct size for overlap-add
    #         overlap_size_resampled = int(overlap_size * self.output_sample_rate / self.input_sample_rate)
    #         if self.buffer.size < overlap_size_resampled:
    #             self.buffer = np.pad(self.buffer, (0, overlap_size_resampled - self.buffer.size), mode='constant')
    #         elif self.buffer.size > overlap_size_resampled:
    #             self.buffer = self.buffer[-overlap_size_resampled:]

    #         # Overlap-add the resampled audio with the buffer
    #         self.buffer[-overlap_size_resampled:] += resampled_audio[:overlap_size_resampled]
    #         self.buffer = np.concatenate([self.buffer, resampled_audio[overlap_size_resampled:]])

    #     # Keep only the last part of the buffer that matches the next expected overlap size
    #     overlap_size_resampled = int(overlap_size * self.output_sample_rate / self.input_sample_rate)
    #     output_audio = self.buffer[:-overlap_size_resampled]
    #     self.buffer = self.buffer[-overlap_size_resampled:]

    #     # Convert numpy array back to bytes and return the resampled audio
    #     return output_audio

    # def resample_overlap_add(self, chunk: bytes) -> bytes:
    #     """Submits a chunk to the resampler, processes it, and handles overlap-add.
    #     Args:
    #         chunk (bytes): A chunk of audio data.
    #     Returns:
    #         bytes: The resampled chunk as bytes.
    #     """
    #     # Convert bytes to numpy array
    #     audio_array = np.frombuffer(chunk, dtype=self.dtype)
    #     chunk_size = audio_array.size
    #     overlap_size = int(chunk_size * self.overlap)

    #     # Create a dynamic window based on the current chunk size
    #     window = hann(chunk_size, sym=False)

    #     # Apply window function to the audio chunk
    #     windowed_audio = audio_array * window

    #     # Overlap-add process
    #     if self.buffer.size == 0:
    #         self.buffer = windowed_audio
    #     else:
    #         # Ensure the buffer has the correct size for overlap-add
    #         if self.buffer.size < overlap_size:
    #             self.buffer = np.pad(self.buffer, (0, overlap_size - self.buffer.size), mode='constant')
    #         elif self.buffer.size > overlap_size:
    #             self.buffer = self.buffer[-overlap_size:]

    #         # Overlap-add the windowed audio with the buffer
    #         self.buffer[-overlap_size:] += windowed_audio[:overlap_size]
    #         self.buffer = np.concatenate([self.buffer, windowed_audio[overlap_size:]])

    #     # Resample the buffered audio
    #     resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')

    #     # Keep only the last part of the buffer that matches the next expected overlap size
    #     self.buffer = self.buffer[-overlap_size:]

    #     # Convert numpy array back to bytes and return the resampled audio
    #     return resampled_buffer[:-overlap_size]

    # def flush(self) -> bytes:
    #     """Flushes the remaining buffer, ensuring all data is resampled and returned."""
    #     if self.buffer.size > 0:
    #         resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')
    #         self.buffer = np.array([], dtype=self.dtype)  # Clear buffer
    #         return resampled_buffer.astype(self.dtype).tobytes()
    #     return b''



    # def resample_overlap_add(self, chunk: bytes) -> bytes:
    #     """Submits a chunk to the resampler, processes it, and handles overlap-add.

    #     Args:
    #         chunk (bytes): A chunk of audio data.

    #     Returns:
    #         bytes: The resampled chunk as bytes.
    #     """
    #     # Convert bytes to numpy array
    #     audio_array = np.frombuffer(chunk, dtype=self.dtype)

    #     chunk_size = audio_array.size
    #     overlap_size = int(chunk_size * self.overlap)

    #     # Create a dynamic window based on the current chunk size
    #     window = hann(chunk_size, sym=False)

    #     # Apply window function to the audio chunk
    #     windowed_audio = audio_array * window

    #     # Prepare the new buffer with padding for overlap
    #     padded_audio = np.pad(windowed_audio, (overlap_size, overlap_size), mode='constant')

    #     # Overlap-add process
    #     if self.buffer.size == 0:
    #         self.buffer = padded_audio
    #     else:
    #         # Ensure buffer is large enough for overlap-add
    #         if self.buffer.size < overlap_size:
    #             # Expand buffer if too short
    #             self.buffer = np.pad(self.buffer, (0, overlap_size - self.buffer.size), mode='constant')
    #         self.buffer[-overlap_size:] += padded_audio[:overlap_size]
    #         self.buffer = np.concatenate([self.buffer, padded_audio[overlap_size:]])

    #     # Resample the buffered audio
    #     resampled_buffer = resampy.resample(self.buffer, self.input_sample_rate, self.output_sample_rate, filter='kaiser_best')

    #     # Keep only the last part of the buffer that matches the next expected overlap size
    #     self.buffer = self.buffer[-overlap_size:]

    #     # Convert numpy array back to bytes
    #     return resampled_buffer

