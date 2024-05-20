from lingu import cfg, log, Logic, repeat
from .handlers.youtube_player import YoutubePlayer
from .state import state
import re

api_key = cfg("music", "google_api_key", env_key="GOOGLE_API_KEY")
no_api_key_msg = \
    "Can't perform that action, Google API Credentials Key is needed."


class MusicLogic(Logic):
    def init(self):
        self.player = None
        if not api_key:
            log.err(
                "[music] Missing Google Google API Credentials Key.\n"
                "  Create a key at https://console.developers.google.com/ and "
                "enable YouTube Data API v3.\n"
                "  Write this key into the 'settings.yaml' file or "
                "set 'GOOGLE_API_KEY' environment variable."
            )
            self.state.set_disabled(True)
        else:
            self.player = YoutubePlayer(
                api_key,
                on_playback_start=self.on_playback_start,
                on_playback_stop=self.on_playback_stop
                )
        self.ready()

    def get_playlist_information(self):
        if not self.player:
            return no_api_key_msg
        return self.player.get_playlist_information()

    def skip_audio(self, skip_count):
        if not isinstance(skip_count, int):
            raise ValueError("skip_count must be an integer")
        if not self.player:
            return no_api_key_msg
        self.player.skip_audio(skip_count)

    def next_song(self):
        if not self.player:
            return no_api_key_msg
        self.player.skip_audio()

    def prev_song(self):
        if not self.player:
            return no_api_key_msg
        self.player.skip_audio(-1)

    def pause(self):
        if not self.player:
            return no_api_key_msg
        return self.player.pause()

    def stop(self):
        if not self.player:
            return no_api_key_msg
        return self.player.stop()

    def volume_up(self):
        if not self.player:
            return no_api_key_msg
        self.player.volume_up()

    def volume_down(self):
        if not self.player:
            return no_api_key_msg
        self.player.volume_down()

    def play_audio_at_playlist_index(self, index):
        if not self.player:
            return no_api_key_msg
        self.player.play_audio_at_playlist_index(index)

    def get_audio_information(self):
        return self.player.update_audio_info()

    def is_playing(self):
        return self.player.is_playing

    @repeat(1)
    def update_ui(self):
        if not self.player or not self.player.is_playing:
            state.info_text = ""
            state.top_info = ""
            state.bottom_info = ""
            return

        audio_information = self.get_audio_information()

        if len(audio_information["playlist"]) > 1:
            state.top_info = \
                f'{str(audio_information["audio_index"] + 1)}/'
            f'{str(len(audio_information["playlist"]))}'

        else:
            state.top_info = ""

        if audio_information:
            state.info_text = self.extract_song_name(audio_information)
            state.bottom_info = self.get_duration_string(audio_information)

    def extract_song_name(self, audio_information):
        # Extract the song name from the audio information
        full_title = audio_information.get("name", "")

        # Split the title at '-', and choose the rightmost part
        if '-' in full_title:
            # Split at the first '-' occurrence
            _, right_part = full_title.split('-', 1)
            # Remove any leading/trailing white spaces
            song_name = right_part.strip()
        else:
            # If there's no '-', use the full title
            song_name = full_title.strip()

        # Remove everything within parentheses
        # Regex to match content within parentheses
        song_name = re.sub(r'\([^)]*\)', '', song_name)

        # Remove any additional white spaces
        # that may have been left after the removal
        song_name = song_name.strip()

        return song_name

    def get_seconds_left(self):
        return self.player.get_seconds_left()

    def get_duration_string(self, audio_information):
        seconds_left = audio_information["seconds_left"]
        if seconds_left > 1:
            return self.format_duration(seconds_left)
        else:
            return ""

    def set_song_position(self, position):
        if not self.player:
            return no_api_key_msg
        self.player.set_song_position(position)

    def on_playback_start(self):
        self.state.set_active(True)
        self.trigger("playback_start")

        log.low("  [music] on_playback_start called")

    def on_playback_stop(self):
        self.state.set_active(False)
        self.trigger("playback_stop")
        log.low("  [music] on_playback_stop called")
        state.bottom_info = ""

    def load_and_play(self, query_or_url, only_playlists=False):
        if not self.player:
            return no_api_key_msg

        return self.player.load_and_play(query_or_url, only_playlists)

    def format_duration(self, seconds):
        # Calculate hours, minutes and seconds
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        s = int(s)
        m = int(m)
        h = int(h)

        if h:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"


logic = MusicLogic()
