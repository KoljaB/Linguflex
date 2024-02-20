from .ui_player import PlayerWidget
from lingu import UI, Line, StretchLine, repeat
from .logic import logic


class MusicUI(UI):
    def __init__(self):
        super().__init__()

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

        self.add(Line())

        label_playlist = UI.label("Playlist")
        self.add(label_playlist)

        self.player_widget = PlayerWidget()
        self.add(self.player_widget)
        self.player_widget.rowClicked.connect(self.play_audio_at_list_index)
        self.player_widget.setMinimumHeight(350)
        self.update_current_song()

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

    @repeat(1)
    def update_current_song(self):
        if not logic.is_playing():
            pass

        audio_information = logic.get_audio_information()

        if not audio_information:
            return

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
