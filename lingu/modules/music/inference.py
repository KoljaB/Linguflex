"""
Music Playout Module

- responsible for playout of songs

"""

from lingu import Populatable
from pydantic import Field
from .logic import logic
import enum


class play_music_by_name(Populatable):
    "Starts music playback of given song or album title; add \"full album\" to search_terms when asked for album; if asked for a specific song call play_audio_at_playlist_index instead if song is in the playlist (you may need to call get_playlist_information to check this)."
    name_or_search_terms: str = Field(None, description="Search terms for music to be played back\nYou can correct the user input (which may contain typos)\nAdd \"full album\" when asked for albums")
    single_song: bool = Field(default=False, description='Set to True if you want to search for a single song')

    def on_populated(self):
        return logic.load_and_play(self.name_or_search_terms, not self.single_song)


class stop_music_playback(Populatable):
    "Stops playback of music"

    def on_populated(self):
        logic.player.stop()
        return "playback stopped"


class pause_or_continue_music(Populatable):
    "Switches between music playback pause mode or continue play mode"

    def on_populated(self):
        logic.player.pause()
        return "music pause mode switched"


class get_playlist_information(Populatable):
    "FIRST call start_music_playback with single_song=False before you call this; ONLY THEN you may retrieve information about that playlist"

    def on_populated(self):
        return logic.player.get_playlist_information()

# @Invokable
# def stop_music_playback():
#     "Stops playback of music"

#     logic.player.stop()
#     return "playback stopped"

# @Invokable
# def pause_or_continue_music():
#     "Switches between music playback pause mode or continue play mode"

#     logic.player.pause()
#     return "music pause mode switched"


# @Invokable
# def get_playlist_information():
#     "FIRST call start_music_playback with single_song=False before you call this; ONLY THEN you may retrieve information about that playlist"

#     return logic.player.get_playlist_information()


class VolumeDirection(enum.Enum):
    """Enumeration representing the direction of the volume change that can be performed, up for noisier und down for quieter."""

    UP = "up"
    DOWN = "down"


class play_music_by_playlist_index(Populatable):
    "FIRST call start_music_playback with single_song=False before you call this; ONLY THEN you may play a an audio from it at the specified index"
    audio_index: int = Field(None, description="Index of audio in playlist to be played")

    def on_populated(self):
        return logic.player.play_audio_at_playlist_index(self.audio_index)


class skip_audio(Populatable):
    "Move to next or previous audio"
    skip_count: int = Field(None, description="Specifies number of tracks to skip, can be positive or negative integer, indicating direction and magnitude.")

    def on_populated(self):
        return logic.player.skip_audio(self.skip_count)


class change_music_volume(Populatable):
    "Changes volume of music playback"
    type: VolumeDirection = Field(None, description="Direction of volume change")

    def on_populated(self):
        if self.type == 'up':
            logic.player.volume_up()
        elif self.type == 'down':
            logic.player.volume_down()
        else:
            return "ERROR: type must be either up or down"

        return "music volume successfully changed"
