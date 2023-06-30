from core import log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MID, DEBUG_LEVEL_ERR

import argparse
import time
import threading
from threading import Thread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import Playlist
import vlc
from yt_dlp import YoutubeDL


class YoutubePlayer:
    def __init__(self, api_key: str):
        self.GOOGLE_CLOUD_API_KEY = api_key
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'

       # Create a new instance of vlc player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_reached_callback)

        self.audio_index = 0
        self.current_playlist = []
        self.is_playlist = False
        self.start_next_audio = False
        self.song_information = None

    def end_reached_callback(self, event):
        self.song_information = None
        log(DEBUG_LEVEL_MAX, f"  [music] song finished, trying to playout next audio from playlist")
        self.start_next_audio = True

    def update_song_info(self):
        total_length = self.player.get_length() / 1000  # get_length() returns in ms, so we convert to seconds
        current_time = self.player.get_time() / 1000  # get_time() returns in ms, so we convert to seconds
        seconds_left = total_length - current_time
        if self.song_information:
            self.song_information["seconds_left_to_play"] = seconds_left        

    def youtube_search(self, query, only_playlists=False, max_results=30):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            developerKey=self.GOOGLE_CLOUD_API_KEY)

        #print (f"youtube_search: {only_playlists}")

        if only_playlists:
            log(DEBUG_LEVEL_MAX, f"  [music] searching for playlists with query '{query}'")
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='playlist'  # This restricts the search to playlists only
            ).execute()
        else:
            log(DEBUG_LEVEL_MAX, f"  [music] searching with query '{query}'")
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results
            ).execute()

        audios = []
        playlists = []
        items = search_response.get('items', [])

        log(DEBUG_LEVEL_MAX, f"  [music] search returned {len(items)} items in total")

        for search_result in items:
            log(DEBUG_LEVEL_MAX, f"  [music] item: {search_result}")
            if search_result['id']['kind'] == 'youtube#video':
                audios.append(f"https://www.youtube.com/watch?v={search_result['id']['videoId']}")
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append(f"https://www.youtube.com/playlist?list={search_result['id']['playlistId']}")

        return audios, playlists
    
    def play_audio(self, url):
        audio_url, audio_title = self.get_audio_title(url)
        
        # Set the media
        log(DEBUG_LEVEL_MAX, f"  [music] playing {audio_title}")
        media = self.instance.media_new(audio_url)
        self.player.set_media(media)

        # Start playing audio
        time.sleep(0.3) # safety wait to let audio cache and not DDOS the video libraries und any circumstances
        self.song_information = {
            "song_playing" : audio_title, 
            "url" : url
        }
        if len(self.current_playlist) > 0:
            self.song_information["playlist_pos"] = f"{self.audio_index+1}/{len(self.current_playlist)}"
            
        self.player.play() 
        return self.song_information 

    def play_playlist(self, url):
        p = Playlist(url)
        self.current_playlist = p.video_urls  # Save the playlist URLs
        self.audio_index = 0  # Update the playlist index
        self.play_audio(self.current_playlist[self.audio_index])

        # New playlist_info list
        playlist_info = []

        # Add position and URL to playlist_info
        for i, song_url in enumerate(self.current_playlist):
            playlist_info.append({
                "pos": i+1, 
                "url": song_url,
            })
            if i > 10: break # huge playlists will flood our context window

        self.song_information["from_playlist"] = playlist_info

        return self.song_information


    def get_audio_title(self, url):
        ydl_opts = {'format': 'bestaudio/best'}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_url = info_dict.get("url", None)
            audio_title = info_dict.get('title', None)

        return audio_url, audio_title               

    def load_and_play(self, query, only_playlists=False):
        try:
            #print (f"load_and_play: {only_playlists}")
            audios, playlists = self.youtube_search(query, only_playlists=only_playlists)

            if only_playlists and not playlists:
                log(DEBUG_LEVEL_MAX, f"  [music] no playlists found.")
                return "No playlists found."
            
            if audios and not only_playlists:
                self.is_playlist = False
                current_playlist = []
                return self.play_audio(audios[0])
            elif playlists:
                p = Playlist(playlists[0])
                self.is_playlist = True
                log(DEBUG_LEVEL_MAX, f"  [music] playlist started ({len(p.video_urls)} audios)")
                return self.play_playlist(playlists[0])
            else:
                log(DEBUG_LEVEL_MAX, f"  [music] no audios or playlists found.")
                return "No audios or playlists found."
        except Exception as e:
            log(DEBUG_LEVEL_MAX, f"  [music] error: {str(e)}")
            return f"Error: {str(e)}"

    def next_audio(self):
        self.start_next_audio = False        
        if not self.is_playlist:
            log(DEBUG_LEVEL_MAX, f"  [music] cannot move to next audio: a single audio is currently playing.")
            return "Error: cannot move to next audio: a single audio is currently playing"

        # Stop the current audio
        self.stop()
        # Increment the playlist index
        self.audio_index += 1
        if self.audio_index < len(self.current_playlist):
            # audio_url, audio_title = self.get_audio_title(self.current_playlist[self.audio_index])
            log(DEBUG_LEVEL_MAX, f"  [music] playlist audio {self.audio_index+1}/{len(self.current_playlist)}")
            return self.play_audio(self.current_playlist[self.audio_index])
        else:
            log(DEBUG_LEVEL_MAX, f"  [music] end of playlist reached")
            return "Error: end of playlist"                
        return f"success, new song playing: {audio_title}"
    
    def previous_audio(self):
        if not self.is_playlist:
            log(DEBUG_LEVEL_MAX, f"  [music] cannot move to previous audio: a single audio is currently playing.")
            return "Error: cannot move to previous audio: a single audio is currently playing"

        # Stop the current audio
        self.stop()
        # Decrement the playlist index
        self.audio_index -= 1
        if self.audio_index >= 0:
            #audio_url, audio_title = self.get_audio_title(self.current_playlist[self.audio_index])
            log(DEBUG_LEVEL_MAX, f"  [music] playlist audio {self.audio_index+1}/{len(self.current_playlist)}")
            return self.play_audio(self.current_playlist[self.audio_index])
        else:
            log(DEBUG_LEVEL_MAX, f"  [music] start of playlist reached")
            return "Error: start of playlist"    

    def pause(self):
        log(DEBUG_LEVEL_MAX, f"  [music] pause player")
        self.player.pause()

    def stop(self):
        log(DEBUG_LEVEL_MAX, f"  [music] stop player")
        self.player.stop()
        time.sleep(0.3) # safety wait to not DDOS the video libraries und any circumstances

    def volume_up(self, increment=20):
        log(DEBUG_LEVEL_MAX, f"  [music] volume up player")
        self.player.audio_set_volume(min(self.player.audio_get_volume() + increment, 100))

    def volume_down(self, decrement=20):
        log(DEBUG_LEVEL_MAX, f"  [music] volume down player")
        self.player.audio_set_volume(max(self.player.audio_get_volume() - decrement, 0))

    def shutdown(self):
        log(DEBUG_LEVEL_MAX, f"  [music] shutdown")
        self.stop()

        # Release the media player instance
        log(DEBUG_LEVEL_MAX, f"  [music] shutdown release player")
        self.player.release()

        # Release the vlc instance
        log(DEBUG_LEVEL_MAX, f"  [music] shutdown release vlc instance")
        self.instance.release()