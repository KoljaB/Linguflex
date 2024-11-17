import pyaudio

# Initialize PyAudio
p = pyaudio.PyAudio()

# Get the number of available audio devices
device_count = p.get_device_count()

print("Available Audio Devices:\n")

# Iterate through all devices and print their details
for i in range(device_count):
    device_info = p.get_device_info_by_index(i)
    print(f"Device Index: {i}")
    print(f"  Name: {device_info['name']}")
    print(f"  Sample Rate (Default): {device_info['defaultSampleRate']} Hz")
    print(f"  Max Input Channels: {device_info['maxInputChannels']}")
    print(f"  Max Output Channels: {device_info['maxOutputChannels']}")
    print(f"  Host API: {p.get_host_api_info_by_index(device_info['hostApi'])['name']}")
    print("\n")

# Terminate the PyAudio instance
p.terminate()
