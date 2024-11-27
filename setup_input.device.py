from pyaudio import paFloat32
import pyaudio
import numpy as np
from textual.app import App, ComposeResult
from textual.widgets import Header, Select, Button, Static
from textual.containers import Horizontal
from textual import on
import wave
import yaml

class InputDeviceSelectorApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p = pyaudio.PyAudio()
        self.input_devices = self.get_input_devices()
        self.selected_device = None
        self.stream = None
        self.output_device_index = None
        self.recorded_frames = []

        # Read output device name from settings.yaml
        with open('lingu/settings.yaml', 'r') as file:
            settings = yaml.safe_load(file)
            output_device_name = settings['speech']['output_device']

        # Get the output device index corresponding to the name
        self.output_device_index = self.get_device_index_by_name(output_device_name)

    def on_mount(self) -> None:
        self.title = "Audio Input Device Selector"
        self.sub_title = "Select, test, and confirm your audio input device"

    def get_input_devices(self):
        return [(self.p.get_device_info_by_index(i)['name'].encode('latin-1').decode('utf-8'), str(i))
                for i in range(self.p.get_device_count())
                if self.p.get_device_info_by_index(i)['maxInputChannels'] > 0]

    def get_device_index_by_name(self, device_name):
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            name = info['name'].encode('latin-1').decode('utf-8')
            if name == device_name:
                return i
        return None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "\n"
            "Steps to follow:\n"
            "1. Select an audio input device from the list below.\n"
            "2. Record a 2 second audio clip to test the device.\n"
            "3. Play back the recording to verify the device's performance.\n"
            "4. Confirm the device if satisfied.\n",
            id="instructions"
        )
        yield Select(options=[(name, index) for name, index in self.input_devices])
        yield Static("")
        yield Static("No device selected.", id="device")
        yield Static("")
        yield Static("Status: Waiting for device selection.", id="status")
        yield Static("")
        yield Horizontal(
            Button("Record from Device", id="record", disabled=True),
            Button("Playback Recording", id="playback", disabled=True),
            Button("Confirm Device", id="confirm", disabled=True),
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.selected_device = int(event.value)
        device_info = self.p.get_device_info_by_index(self.selected_device)

        # Get supported sample rates for the device
        self.supported_rates = self.get_supported_sample_rates(self.selected_device)

        # Format the device information nicely
        device_details = (
            f"Device Selected:\n"
            f"Name: {device_info['name']}\n"
            f"Default Sample Rate: {device_info['defaultSampleRate']} Hz\n"
            f"Max Input Channels: {device_info['maxInputChannels']}\n"
            f"Supported Sample Rates: {', '.join(map(str, self.supported_rates))} Hz"
        )

        self.query_one("#device").update(device_details)
        self.query_one("#status").update("Device selected. You can now record audio.")
        self.query_one("#record").disabled = False
        self.query_one("#confirm").disabled = False        

    def get_supported_sample_rates(self, device_index):
        # Sample rates to check for support
        standard_rates = [8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
        supported_rates = []
        for rate in standard_rates:
            try:
                if self.p.is_format_supported(rate,
                                              input_device=device_index,
                                              input_channels=1,
                                              input_format=paFloat32):
                    supported_rates.append(rate)
            except ValueError:
                continue
        return supported_rates

    @on(Button.Pressed, "#record")
    def record_audio(self) -> None:
        try:
            self.query_one("#record").disabled = True
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            highest_rate = max(self.supported_rates)
            self.recorded_frames = []
            CHUNK = 1024
            FORMAT = pyaudio.paFloat32
            CHANNELS = 1
            RECORD_SECONDS = 2

            # Open input stream for recording
            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=highest_rate,
                input=True,
                input_device_index=self.selected_device,
                frames_per_buffer=CHUNK
            )

            self.query_one("#status").update(f"Recording for {RECORD_SECONDS} second(s)...")
            for _ in range(0, int(highest_rate / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.recorded_frames.append(data)
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.query_one("#status").update("[green]Recording completed.[/green] You can now play back the recording.")
            self.query_one("#playback").disabled = False
        except Exception as e:
            self.query_one("#status").update(f"[red]Failed to record audio: {e}[/red]")
        self.query_one("#record").disabled = False

    @on(Button.Pressed, "#playback")
    def playback_audio(self) -> None:
        try:
            if self.output_device_index is not None:
                highest_rate = max(self.supported_rates)
                CHUNK = 1024
                FORMAT = pyaudio.paFloat32
                CHANNELS = 1

                # Open output stream for playback
                playback_stream = self.p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=highest_rate,
                    output=True,
                    output_device_index=self.output_device_index,
                    frames_per_buffer=CHUNK
                )

                self.query_one("#status").update("[green]Playing back recording...[/green]")
                for data in self.recorded_frames:
                    playback_stream.write(data)
                playback_stream.stop_stream()
                playback_stream.close()
                self.query_one("#status").update("[green]Playback completed.[/green]")
            else:
                self.query_one("#status").update("[red]Output device not found.[/red] Cannot play back recording.")
        except Exception as e:
            self.query_one("#status").update(f"[red]Failed to play back audio: {e}[/red]")

    @on(Button.Pressed, "#confirm")
    def confirm_device(self) -> None:
        if self.selected_device is not None:
            device_info = self.p.get_device_info_by_index(self.selected_device)
            device_name = device_info['name']

            # Load settings.yaml
            with open('lingu/settings.yaml', 'r') as file:
                settings = yaml.safe_load(file)

            # Update the input_device field
            settings['listen']['input_device'] = device_name

            # Save the updated settings
            with open('lingu/settings.yaml', 'w') as file:
                yaml.safe_dump(settings, file)

            self.query_one("#status").update(
                f"[green]Device confirmed.[/green]\n"
                f"Device Name: {device_name}\n"
                "Thank you for using the Audio Input Device Selector."
            )
            print(f"Confirmed input device: {device_name}")
            self.exit()

    def on_stop(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    app = InputDeviceSelectorApp()
    app.run()
