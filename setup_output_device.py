from pyaudio import paFloat32
import pyaudio
import numpy as np
from textual.app import App, ComposeResult
from textual.widgets import Header, Select, Button, Static
from textual.containers import Horizontal
from textual import on
import wave
import yaml

class OutputDeviceSelectorApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p = pyaudio.PyAudio()
        self.output_devices = self.get_output_devices()
        self.selected_device = None
        self.stream = None

    def on_mount(self) -> None:
        self.title = "Audio Device Selector"
        self.sub_title = "Select, test, and confirm your audio output device"

    def get_output_devices(self):
        return [(self.p.get_device_info_by_index(i)['name'].encode('latin-1').decode('utf-8'), str(i))
                for i in range(self.p.get_device_count())
                if self.p.get_device_info_by_index(i)['maxOutputChannels'] > 0]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "\n"
            "Steps to follow:\n"
            "1. Select an audio output device from the list below.\n"
            "2. Test the device by playing a sine wave or a WAV file.\n"
            "3. If you're satisfied with the device's performance, confirm your selection.\n",
            id="instructions"
        )
        yield Select(options=[(name, index) for name, index in self.output_devices])
        yield Static("")
        yield Static("No device selected.", id="device")
        yield Static("")
        yield Static("Status: Waiting for device selection.", id="status")
        yield Static("")
        yield Horizontal(
            Button("Play Sine Wave", id="test", disabled=True),
            Button("Play WAV File", id="play_wav", disabled=True),
            Button("Confirm Device", id="confirm", disabled=True),
        )

    def generate_test_tone(self, sample_rate, duration=1):
        # Generate a 440Hz sine wave
        samples = np.arange(duration * sample_rate)
        tone = np.sin(2 * np.pi * 440 * samples / sample_rate).astype(np.float32)
        return tone

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
            f"Max Output Channels: {device_info['maxOutputChannels']}\n"
            f"Supported Sample Rates: {', '.join(map(str, self.supported_rates))} Hz"
        )
        
        self.query_one("#device").update(device_details)
        self.query_one("#status").update("Device selected. You can now test the audio output.")
        self.query_one("#test").disabled = False
        self.query_one("#play_wav").disabled = False
        self.query_one("#confirm").disabled = False

    def get_supported_sample_rates(self, device_index):
        # Sample rates to check for support
        standard_rates = [8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]
        supported_rates = []
        for rate in standard_rates:
            try:
                if self.p.is_format_supported(rate,
                                              output_device=device_index,
                                              output_channels=1,
                                              output_format=paFloat32):
                    supported_rates.append(rate)
            except ValueError:
                continue
        return supported_rates

    @on(Button.Pressed, "#test")
    def test_device(self) -> None:
        try:
            self.query_one("#test").disabled = True
            self.query_one("#play_wav").disabled = True
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            highest_rate = max(self.supported_rates)
            tone = self.generate_test_tone(highest_rate)
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=highest_rate,
                output=True,
                output_device_index=self.selected_device,
                frames_per_buffer=1024
            )

            self.query_one("#status").update(f"Playing a 440Hz sine wave at {highest_rate} Hz sample rate...")
            self.stream.write(tone.tobytes())
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.query_one("#status").update(
                "[green]Sine wave played successfully.[/green]\n"
                "Did you hear the sound? If yes, you can proceed to confirm the device."
            )
        except Exception as e:
            self.query_one("#status").update(f"[red]Failed to play sine wave: {e}[/red]")
        self.query_one("#test").disabled = False
        self.query_one("#play_wav").disabled = False

    @on(Button.Pressed, "#confirm")
    def confirm_device(self) -> None:
        if self.selected_device is not None:
            device_info = self.p.get_device_info_by_index(self.selected_device)
            device_name = device_info['name']

            # Load settings.yaml
            with open('lingu/settings.yaml', 'r') as file:
                settings = yaml.safe_load(file)

            # Update the output_device field
            settings['speech']['output_device'] = device_name

            # Save the updated settings
            with open('lingu/settings.yaml', 'w') as file:
                yaml.safe_dump(settings, file)

            self.query_one("#status").update(
                f"[green]Device confirmed.[/green]\n"
                f"Device Index: {self.selected_device}\n"
                "Thank you for using the Audio Device Selector."
            )
            print(f"Confirmed device index: {self.selected_device}")
            self.exit()

    @on(Button.Pressed, "#play_wav")
    def play_wav_file(self) -> None:
        try:
            self.query_one("#test").disabled = True
            self.query_one("#play_wav").disabled = True
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            wf = wave.open('test_audio.wav', 'rb')
            self.stream = self.p.open(
                format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=self.selected_device if self.selected_device is not None else None
            )

            self.query_one("#status").update("Playing 'test_audio.wav' file...")
            data = wf.readframes(1024)
            while data:
                self.stream.write(data)
                data = wf.readframes(1024)
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            wf.close()
            self.query_one("#status").update(
                "[green]WAV file played successfully.[/green]\n"
                "Did you hear the audio? If yes, you can proceed to confirm the device."
            )
        except Exception as e:
            self.query_one("#status").update(f"[red]Failed to play WAV file: {e}[/red]")
        self.query_one("#test").disabled = False
        self.query_one("#play_wav").disabled = False

    def on_stop(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    app = OutputDeviceSelectorApp()
    app.run()
