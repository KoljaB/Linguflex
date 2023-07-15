from pygame import mixer
from queue import Queue
from threading import Thread

AUDIO_FILES = [
    "resources/start_system.mp3",
    "resources/error.mp3",
    "resources/function_executing.wav",
    "resources/function_fail.mp3",
    "resources/function_success.wav",
    "resources/new_mail.mp3",
    "resources/creating_output.wav",
    "resources/creating_output_short.wav",
    "resources/recording_stop.wav",
    "resources/recording_start.wav",
    "resources/shutdown.wav",
    "resources/notice.wav",
    "resources/before_answer.wav",
]

class SoundPlayer:
    def __init__(self):
        mixer.init()
        self.queue = Queue()
        self.thread = Thread(target=self._play_sounds_from_queue)
        self.thread.daemon = True
        self.thread.start()

    def add_sound(self, sound_name: str):
        file_name = next((name for name in AUDIO_FILES if sound_name in name), None)
        if file_name:
            self.queue.put(file_name)
        else:
            print(f"Sound file '{sound_name}' not found.")
        
    def _play_sounds_from_queue(self):
        while True:
            file_name = self.queue.get()
            mixer.music.load(file_name)
            mixer.music.play()
            while mixer.music.get_busy():
                continue
            self.queue.task_done()

    def _cleanup(self):
        # Stop the sound player thread and wait for it to finish
        self.queue.join()
        mixer.quit()            

_sound_player = SoundPlayer()

def play_sound(sound_name: str):
    _sound_player.add_sound(sound_name)

def shutdown_sound():
    _sound_player._cleanup()
