from core import BaseModule, Request, cfg,  log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX

from linguflex_functions import linguflex_function, LinguFlexBase
from pydantic import Field
import enum

from media_playout_helper import YoutubePlayer
player = YoutubePlayer(cfg("api_key", env_key="GOOGLE_API_KEY"))

class start_music_playback(LinguFlexBase):
    "Starts music playback of given song or album title; add \"full album\" to search_terms when asked for album; if asked for a specific song call play_audio_at_playlist_index instead if song is in the playlist (you may need to call get_playlist_information to check this)."
    query_or_url: str = Field(..., description="Search terms for music to be played back; optimize user input which may contain typos; add \"full album\" when asked for albums; can also take urls")
    single_song: bool = Field(default=False, description='Set to True if asked to search for a single song')

    def execute(self):
        return player.load_and_play(self.query_or_url, not self.single_song)  

@linguflex_function
def stop_music_playback():
    "Stops playback of music"

    player.stop() 
    return "playback stopped"


@linguflex_function
def pause_or_continue_music():
    "Switches between music playback pause mode or continue play mode"

    player.pause() 
    return "music pause mode switched"

class play_audio_at_index(LinguFlexBase):
    "FIRST call start_music_playback with single_song=False before you call this; ONLY THEN you may play a an audio from it at the specified index"
    audio_index: int = Field(..., description="Index of audio in playlist to be played")

    def execute(self):
        return player.play_audio_at_playlist_index(self.audio_index) 

class skip_audio(LinguFlexBase):
    "Move to next or previous audio"
    skip_count: int = Field(..., description="Specifies number of tracks to skip, can be positive or negative integer, indicating direction and magnitude.")

    def execute(self):
        return player.skip_audio(self.skip_count) 

@linguflex_function
def get_playlist_information():
    "FIRST call start_music_playback with single_song=False before you call this; ONLY THEN you may retrieve information about that playlist"

    return player.get_playlist_information() 

class VolumeDirection(str, enum.Enum):
    """Enumeration representing the direction of the volume change that can be performed, up for noisier und down for quieter."""

    UP = "up"
    DOWN = "down"

class change_music_volume(LinguFlexBase):
    "Changes volume of music playback"
    type: VolumeDirection = Field(..., description="Direction of volume change")

    def execute(self):
        if self.type == 'up':
            player.volume_up()
        elif self.type == 'down':
            player.volume_down()
        else:
            return "ERROR: type must be either up or down"

        return "music volume successfully changed"


class PlayoutHandler(BaseModule):
    def init(self) -> None: 
        self.server.register_event("playlist_index", player.play_audio_at_playlist_index)
        self.server.register_event("volume_up", player.volume_up)
        self.server.register_event("volume_down", player.volume_down)
        self.server.register_event("skip_audio", player.skip_audio)
        self.server.register_event("pause_continue", player.pause)
        self.server.register_event("stop", player.stop)

    def cycle(self, 
            request: Request) -> None: 
        player.cycle()

        if player.audio_information:
            audio_information = player.update_audio_info()
            self.server.set_event("audio_information", audio_information)
            request.add_prompt(f'Song: "{audio_information["name"]}", Link: "{audio_information["url"]}.')
    def shutdown(self) -> None:
        player.shutdown()