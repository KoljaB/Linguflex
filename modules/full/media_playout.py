from core import BaseModule, Request, cfg
from linguflex_functions import linguflex_function, LinguFlexBase
from pydantic import Field
import enum

from media_playout_helper import YoutubePlayer
player = YoutubePlayer(cfg("api_key", registry_name="GOOGLE_API_KEY"))

class start_music_playback(LinguFlexBase):
    "Starts music playback of the given song or album title; add \"full album\" to search_terms when asked for album"
    search_terms: str = Field(..., description="Search terms for the music to be played out; add \"full album\" when asked for albums")
    only_playlists: bool = Field(default=False, description='Set to True if you only want to look for playlists')

    def execute(self):
        songname_played = player.load_and_play(self.search_terms, self.only_playlists)  
        return {'result': 'playback started', 'name': songname_played}


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

@linguflex_function
def play_next_audio():
    "Plays the next audio from the playlist"

    return player.next_audio() 

@linguflex_function
def play_previous_audio():
    "Plays the previous audio from the playlist"

    return player.previous_audio() 


class VolumeDirection(str, enum.Enum):
    """Enumeration representing the direction of the volume change that can be performed, up for noisier und down for quieter."""

    UP = "up"
    DOWN = "down"

class change_music_volume(LinguFlexBase):
    "Changes volume of music playout"
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
    def cycle(self, 
            request: Request) -> None: 
        if player.start_next_audio: 
            player.next_audio()
        if not player.song_information is None:
            player.update_song_info()
            request.prompt += f'The song currently playing is named "{player.song_information["name"]}", url is "{player.song_information["url"]}. '
    def shutdown(self) -> None:
        player.shutdown()