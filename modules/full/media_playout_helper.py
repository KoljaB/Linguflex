from core import log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MID, DEBUG_LEVEL_ERR

import argparse
import time
import threading
import urllib.parse
from threading import Thread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import Playlist
import traceback
import vlc
import copy
from yt_dlp import YoutubeDL

MAX_NUMBER_OF_PLAYLIST_SONGS = 20

class PlaylistInfoGrabberThread(Thread):
    def __init__(self, youtube_player):
        Thread.__init__(self)
        self.youtube_player = youtube_player
        self.is_running = True
        self.songs_processed = 0  
        self.songs_processed_finished = False

    def run(self):
        while self.is_running:
            if self.youtube_player.new_playlist_loaded:
                self.songs_processed = 0
                self.youtube_player.new_playlist_loaded = False  
            if self.youtube_player.is_playlist and self.songs_processed < MAX_NUMBER_OF_PLAYLIST_SONGS and not self.songs_processed_finished:
                for url in self.youtube_player.playlist_audio_urls:
                    if self.songs_processed >= MAX_NUMBER_OF_PLAYLIST_SONGS or self.songs_processed >= len(self.youtube_player.playlist_audio_urls):
                        break
                    info = self.youtube_player.get_audio_info(url)
                    if not self.is_running or self.youtube_player.new_playlist_loaded:
                        break
                    self.youtube_player.current_playlist.append(info)
                    self.songs_processed += 1  
                    time.sleep(1)  
            time.sleep(1)        

    def shutdown(self):
        self.is_running = False

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
        self.playlist_audio_urls = []
        self.is_playlist = False
        self.start_next_audio = False
        self.audio_information = None
        self.new_playlist_loaded = False

        self.playlist_info_grabber_thread = PlaylistInfoGrabberThread(self)
        self.playlist_info_grabber_thread.start()

    def load_and_play(self, query_or_url, only_playlists=False):
        try:
            parsed = urllib.parse.urlparse(query_or_url)
            
            if parsed.netloc == 'www.youtube.com':
                query_params = urllib.parse.parse_qs(parsed.query)

                # single audio handling
                if 'v' in query_params and not only_playlists: 
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    log(DEBUG_LEVEL_MAX, f"  [music] single audio playback started")
                    self.playlist_audio_urls.append(query_or_url)
                    return self.play_audio(query_or_url)
                
                # playlist handling
                elif 'list' in query_params:
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    p = Playlist(query_or_url)
                    playlist_title = self.get_playlist_details(query_or_url)
                    log(DEBUG_LEVEL_MAX, f"  [music] playlist started ({len(p.video_urls)} audios)")
                    return self.play_playlist(query_or_url, playlist_title)
                
                else:
                    log(DEBUG_LEVEL_MAX, f"  [music] invalid YouTube URL.")
                    return "Invalid YouTube URL."
            else:
                audios, playlists = self.youtube_search(query_or_url, only_playlists=only_playlists)

                if only_playlists and not playlists:
                    log(DEBUG_LEVEL_MAX, f"  [music] no playlists found.")
                    return "No playlists found."
                
                self.current_playlist = []
                self.playlist_audio_urls = []

                if audios and not only_playlists:
                    self.is_playlist = True
                    self.new_playlist_loaded = True 
                    log(DEBUG_LEVEL_MAX, f"  [music] single audio playback started")
                    self.playlist_audio_urls.append(audios[0])
                    return self.play_audio(audios[0])                
                elif playlists:
                    p = Playlist(playlists[0])
                    self.is_playlist = True
                    self.new_playlist_loaded = True 
                    playlist_title = self.get_playlist_details(playlists[0])
                    log(DEBUG_LEVEL_MAX, f"  [music] playlist started ({len(p.video_urls)} audios)")
                    return self.play_playlist(playlists[0], playlist_title)
                else:
                    log(DEBUG_LEVEL_MAX, f"  [music] no audios or playlists found.")
                    return "No audios or playlists found."
        except Exception as e:
            log(DEBUG_LEVEL_MAX, f"  [music] error: {str(e)}")
            traceback.print_exc()
            return f"Error: {str(e)}"

        
    def get_playlist_details(self, playlist_url):
        # Extract playlist ID from the URL
        playlist_id = playlist_url.split('=')[1]

        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            developerKey=self.GOOGLE_CLOUD_API_KEY)
        
        # Call the YouTube API to get playlist details
        playlist_response = youtube.playlists().list(
            part='snippet',
            id=playlist_id
        ).execute()

        if playlist_response['items']:
            # Return playlist title
            return playlist_response['items'][0]['snippet']['title']

        return None        

    def youtube_search(self, query, only_playlists=False, max_results=30):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
            developerKey=self.GOOGLE_CLOUD_API_KEY)

        if only_playlists:
            log(DEBUG_LEVEL_MAX, f"  [music] searching for playlists with query '{query}'")
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='playlist' 
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
            if search_result['id']['kind'] == 'youtube#video':
                audios.append(f"https://www.youtube.com/watch?v={search_result['id']['videoId']}")
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append(f"https://www.youtube.com/playlist?list={search_result['id']['playlistId']}")

        return audios, playlists
    
    def play_audio(self, url, playlist_url="No playlist active", playlist_title="No playlist active"):
        try:
            audio_url, audio_title, audio_length, audio_description = self.fetch_audio_information(url)
            
            # Set the media
            media = self.instance.media_new(audio_url)
            self.player.set_media(media)

            # Start playing audio
            time.sleep(0.3) # safety wait to let audio cache and not DDOS the video libraries und any circumstances
            self.audio_information = {
                "name" : audio_title, 
                "url" : url
            }
            if len(self.playlist_audio_urls) > 0:
                self.audio_information["playlist_pos"] = f"{self.audio_index+1}/{len(self.playlist_audio_urls)}"
                self.audio_information["playlist_url"] = playlist_url
                self.audio_information["playlist_title"] = playlist_title

            log_text = f"  [music] playing {audio_title}"
            if self.is_playlist: log_text += f'  / playlist pos {self.audio_information["playlist_pos"]}'
            log(DEBUG_LEVEL_MAX, log_text)
            self.player.play() 

            return { 
                "result" : "playback started",
                "audio_information" : self.audio_information
            }
        except Exception as e:
            log(DEBUG_LEVEL_MAX, f"  [music] error: {str(e)}")
            return f"Error: {str(e)}"
    
    def play_playlist(self, url, playlist_title=None):
        p = Playlist(url)
        self.playlist_audio_urls = list(p.video_urls)[:MAX_NUMBER_OF_PLAYLIST_SONGS]
        self.audio_index = 0 
        return self.play_audio(self.playlist_audio_urls[self.audio_index], url, playlist_title)

    def fetch_audio_information(self, url):
        # disabled logging
        # ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'logger': None } 

        # enabled logging 
        ydl_opts = {'format': 'bestaudio/best'} 


        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_url = info_dict.get("url", None)
            audio_title = info_dict.get('title', None)
            audio_length = info_dict.get('duration', None)
            audio_description = info_dict.get('description', None)

        return audio_url, audio_title, audio_length, audio_description


    def end_reached_callback(self, event):
        self.audio_information["name"] = ""
        self.audio_information["url"] = ""
        log(DEBUG_LEVEL_MAX, f"  [music] track end reached")
        self.start_next_audio = True

    def cycle(self):
        if self.start_next_audio: 
             self.start_next_audio = False
             self.skip_audio()

    def update_audio_info(self):
        audio_info_copy = None
        if self.audio_information is not None:
            self.audio_information["playing"] = self.player.is_playing()             
            self.audio_information["audio_index"] = self.audio_index
            total_length = self.player.get_length() / 1000 
            current_time = self.player.get_time() / 1000  

            seconds_left = total_length - current_time
            if self.audio_information:
                self.audio_information["total_length"] = total_length        
                self.audio_information["current_time"] = current_time        
                self.audio_information["seconds_left"] = seconds_left

            audio_info_copy = copy.deepcopy(self.audio_information)
            audio_info_copy["playlist"] = self.current_playlist

        return audio_info_copy
    
    def get_audio_info(self, url):
        audio_url, audio_title, audio_length, audio_description = self.fetch_audio_information(url)
        return {
            "title": audio_title[:45],
            "url": url[:30],
            "length": audio_length,
        }    

    def play_audio_at_playlist_index(self, index):
        if not self.is_playlist:
            log(DEBUG_LEVEL_MAX, f"  [music] cannot play audio: no playlist active")
            return "Error: no playlist active"
            
        if index >= len(self.playlist_audio_urls) or index < 0:
            log(DEBUG_LEVEL_MAX, f"  [music] index out of range")
            return f"Error: index out of range. Index should be between 0 and {len(self.playlist_audio_urls)-1}"
            
        self.audio_index = index
        log(DEBUG_LEVEL_MAX, f"  [music] playlist audio {self.audio_index+1}/{len(self.playlist_audio_urls)}")
        return self.play_audio(self.playlist_audio_urls[self.audio_index])


    def get_playlist_information(self):
        return self.audio_information

    def skip_audio(self, skip_count=1):
        if not self.is_playlist:
            log(DEBUG_LEVEL_MAX, f"  [music] cannot move to next or previous audio: no playlist active")
            return "Error: no playlist active"

        # Increment or decrement the index based on the skip_count
        self.audio_index += skip_count
        return self.play_audio_at_playlist_index(self.audio_index)        
        
    def pause(self):
        log(DEBUG_LEVEL_MAX, f"  [music] pause player")
        self.player.pause()

    def stop(self):
        log(DEBUG_LEVEL_MAX, f"  [music] stop player and rewind to start")
        self.player.set_time(0)  
        if self.player.is_playing(): 
            self.player.pause()  

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

        self.playlist_info_grabber_thread.shutdown()
        self.playlist_info_grabber_thread.join()