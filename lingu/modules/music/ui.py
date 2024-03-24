from lingu import UI, Line, StretchLine, repeat
from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt
from .ui_player import PlayerWidget
from .logic import logic
from qfluentwidgets import Slider, setTheme, Theme, ComboBox, ProgressBar


class MusicUI(UI):
    def __init__(self):
        super().__init__()

        self.slider_upgrade_allowed = True

        label = UI.headerlabel("🎶 Music")
        self.header(label, nostyle=True)

        self.buttons = self.add_buttons({
            "pause":
                ("⏯️", self.pause),
            "stop":
                ("⏹️", self.stop),
            "volume_up":
                ("🔊", self.volume_up),
            "volume_down":
                ("🔉", self.volume_down),
            "previous":
                ("◀", self.previous_song),
            "next":
                ("▶", self.next_song),
        })

        self.playlist_position = UI.headerlabel("# 0/0 ")
        self.header(self.playlist_position, align="right", nostyle=True)

        line = StretchLine()
        label_songname = UI.label("Title")
        line.add(label_songname)
        self.song_name = UI.label("", "content")
        line.add(self.song_name)
        label_time = UI.label("Time")
        line.add(label_time, align="right")
        self.time = UI.label("", "content")
        line.add(self.time, align="right")
        self.add(line)

        # self.add(Line())
        self.progress_bar = Slider(Qt.Orientation.Horizontal)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.sliderPressed.connect(self.on_slider_pressed)
        self.progress_bar.sliderReleased.connect(self.on_slider_released)
        self.add(self.progress_bar)  # Add to the layout at the desired position

        label_playlist = UI.label("Playlist")
        self.add(label_playlist)

        self.player_widget = PlayerWidget()
        self.add(self.player_widget)
        self.player_widget.rowClicked.connect(self.play_audio_at_list_index)
        self.player_widget.setMinimumHeight(350)
        self.update_current_song()

    def on_slider_pressed(self):
        # Disconnect the update to avoid conflicts
        self.slider_upgrade_allowed = False

    def on_slider_released(self):
        # Reconnect the update signal

        # Logic to set the song's position based on slider value
        logic.set_song_position(self.progress_bar.value())
        self.slider_upgrade_allowed = True

    def previous_song(self):
        logic.prev_song()

    def next_song(self):
        logic.next_song()

    def pause(self):
        logic.pause()

    def stop(self):
        logic.stop()

    def volume_up(self):
        logic.volume_up()

    def volume_down(self):
        logic.volume_down()

    def play_audio_at_list_index(self, index):
        logic.play_audio_at_playlist_index(index)
    
    def reset_bars(self):
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)

    @repeat(1)
    def update_current_song(self):
        if not logic.is_playing():
            self.reset_bars()
            return

        audio_information = logic.get_audio_information()

        if not audio_information:
            self.reset_bars()
            return

        if ("seconds_left" in audio_information
                and "total_length" in audio_information):

            if self.slider_upgrade_allowed:
                seconds_left = audio_information["seconds_left"]
                total_duration = audio_information["total_length"]
                self.progress_bar.setMaximum(int(total_duration))
                current_time = total_duration - seconds_left

                if total_duration > 0 and current_time > 0:
                    self.progress_bar.setValue(int(current_time))
                else:
                    self.progress_bar.setValue(0)
        
        else:
            self.reset_bars()

        self.player_widget.display(audio_information)

        if len(audio_information["playlist"]) > 1:
            self.playlist_position.setText(
                f'# {str(audio_information["audio_index"] + 1)}/'
                f'{str(len(audio_information["playlist"]))} '
            )
        else:
            self.playlist_position.setText("")

        self.song_name.setText(audio_information["name"])
        duration_string = logic.get_duration_string(audio_information)
        if duration_string:
            self.time.setText(duration_string)
        else:
            self.time.setText("")
