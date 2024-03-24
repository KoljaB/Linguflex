from googleapiclient.discovery import build
from lingu import cfg, log, notify
from threading import Thread
from yt_dlp import YoutubeDL
from pytube import Playlist
import urllib.parse
import traceback
import threading
import copy
import time
import vlc

max_playlist_songs = cfg("music", "max_playlist_songs", default=20)


class PlaylistInfoGrabberThread(Thread):
    def __init__(self, youtube_player):
        Thread.__init__(self)
        self.daemon = True
        self.youtube_player = youtube_player
        self.is_running = True
        self.songs_processed = 0
        self.songs_processed_finished = False

    def run(self):
        while self.is_running:
            if self.youtube_player.new_playlist_loaded:
                self.songs_processed = 0
                self.youtube_player.new_playlist_loaded = False

            if (self.youtube_player.is_playlist
                    and self.songs_processed < max_playlist_songs
                    and not self.songs_processed_finished):

                for url in self.youtube_player.playlist_audio_urls:
                    if (self.songs_processed >= max_playlist_songs
                        or self.songs_processed >=
                            len(self.youtube_player.playlist_audio_urls)):
                        break
                    info = self.youtube_player.get_audio_info(url)
                    if (not self.is_running
                            or self.youtube_player.new_playlist_loaded):
                        break
                    self.youtube_player.current_playlist.append(info)
                    self.songs_processed += 1
                    time.sleep(1)
            time.sleep(1)

    def shutdown(self):
        self.is_running = False


class YoutubePlayer:

    def __init__(
            self,
            api_key: str,
            on_playback_start=None,
            on_playback_stop=None
    ):
        self.on_playback_start = on_playback_start
        self.on_playback_stop = on_playback_stop

        self.GOOGLE_CLOUD_API_KEY = api_key
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'

        self.instance = vlc.Instance("--verbose=-1 --audio-resampler=soxr "
                                     "--network-caching=5000 --avcodec-hw=any")
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.end_reached_callback)

        self.audio_index = 0
        self.current_playlist = []
        self.playlist_audio_urls = []
        self.is_playlist = False
        self.audio_information = None
        self.new_playlist_loaded = False
        self.is_playing = False

        self.playlist_info_grabber_thread = PlaylistInfoGrabberThread(self)
        self.playlist_info_grabber_thread.start()

    def end_reached_callback(self, event):
        """
        Callback called when the end of a media is reached.
        This gets called after every song in a playlist.
        """
        self.audio_information["name"] = ""
        self.audio_information["url"] = ""
        log.inf("  [music] track end reached")

        # Use a timer to delay the playback initiation
        if (self.is_playlist
                and self.audio_index + 1 < len(self.playlist_audio_urls)):
            threading.Timer(0.1, self.skip_audio).start()
        else:
            self.is_playing = False
            if self.on_playback_stop:
                self.on_playback_stop()

    def load_and_play(self, query_or_url, only_playlists=False):
        log.inf(f"  [music] load and play {query_or_url}")
        try:
            parsed = urllib.parse.urlparse(query_or_url)

            if parsed.netloc == 'www.youtube.com':
                query_params = urllib.parse.parse_qs(parsed.query)

                # single audio handling
                if 'v' in query_params and not only_playlists:
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    log.inf("  [music] single audio playback started")
                    self.playlist_audio_urls.append(query_or_url)
                    return self.play_audio(query_or_url)

                # playlist handling
                elif 'list' in query_params:
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    p = Playlist(query_or_url)
                    playlist_title = self.get_playlist_details(query_or_url)
                    log.inf(f"  [music] playlist started ({len(p.video_urls)} "
                            "audios)")
                    return self.play_playlist(query_or_url, playlist_title)

                else:
                    log.inf("  [music] invalid YouTube URL.")
                    return "Invalid YouTube URL."
            else:
                audios, playlists = self.youtube_search(
                    query_or_url,
                    only_playlists=only_playlists)

                if only_playlists and not playlists:
                    log.inf("  [music] no playlists found.")
                    return "No playlists found."

                self.current_playlist = []
                self.playlist_audio_urls = []

                if audios and not only_playlists:
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    log.inf("  [music] single audio playback started")
                    self.playlist_audio_urls.append(audios[0])
                    return self.play_audio(audios[0])

                elif playlists:
                    p = Playlist(playlists[0])
                    self.is_playlist = True
                    self.new_playlist_loaded = True
                    playlist_title = self.get_playlist_details(playlists[0])
                    log.inf(f"  [music] playlist started ({len(p.video_urls)} "
                            "audios)")
                    return self.play_playlist(playlists[0], playlist_title)
                else:
                    log.inf("  [music] no audios or playlists found.")
                    return "No audios or playlists found."
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            traceback.print_exc()
            return f"Error: {str(e)}"

    def get_playlist_details(self, playlist_url):
        playlist_id = playlist_url.split('=')[1]

        # Call the YouTube API to get playlist details
        youtube = build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.GOOGLE_CLOUD_API_KEY)

        playlist_response = youtube.playlists().list(
            part='snippet',
            id=playlist_id
        ).execute()

        if playlist_response['items']:
            # Return playlist title
            return playlist_response['items'][0]['snippet']['title']

        return None

    def youtube_search(self, query, only_playlists=False, max_results=30):
        youtube = build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.GOOGLE_CLOUD_API_KEY)

        if only_playlists:
            log.inf(f"  [music] searching for playlists with query '{query}'")
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='playlist'
            ).execute()
        else:
            log.inf(f"  [music] searching with query '{query}'")
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results
            ).execute()

        audios = []
        playlists = []
        items = search_response.get('items', [])

        log.inf(f"  [music] search returned {len(items)} items in total")

        for search_result in items:
            if search_result['id']['kind'] == 'youtube#video':
                audios.append("https://www.youtube.com/watch?"
                              f"v={search_result['id']['videoId']}")
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append("https://www.youtube.com/playlist?"
                                 f"list={search_result['id']['playlistId']}")

        return audios, playlists

    def play_audio(
            self,
            url,
            playlist_url="No playlist active",
            playlist_title="No playlist active"):
        try:
            audio_url, audio_title, audio_length, audio_description = \
                self.fetch_audio_information(url)

            media = self.instance.media_new(audio_url)
            self.player.set_media(media)

            time.sleep(0.3)  # safety wait to let audio cache
            self.audio_information = {
                "name": audio_title,
                "url": url
            }
            if len(self.playlist_audio_urls) > 0:
                self.audio_information["playlist_pos"] = f"{self.audio_index+1}/{len(self.playlist_audio_urls)}"
                self.audio_information["playlist_url"] = playlist_url
                self.audio_information["playlist_title"] = playlist_title

            log_text = f"  [music] playing {audio_title}"
            if self.is_playlist:
                log_text += f'  / playlist pos {self.audio_information["playlist_pos"]}'
            log.inf(log_text)

            if not self.is_playing:
                self.is_playing = True
                if self.on_playback_start:
                    self.on_playback_start()

            notify(
                "Now playing:",
                f"\"{audio_title}\"",
                10000,
                "success"
            )
            self.player.play()

            return { 
                "result" : "playback started",
                "audio_information" : self.audio_information
            }
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            return f"Error: {str(e)}"

    def play_playlist(self, url, playlist_title=None):
        p = Playlist(url)
        self.playlist_audio_urls = list(p.video_urls)[:max_playlist_songs]
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
            "title": audio_title[:70],
            "url": url[:40],
            "length": audio_length,
        }

    def play_audio_at_playlist_index(self, index):
        if not self.is_playlist:
            log.inf("  [music] cannot play audio: no playlist active")
            return "Error: no playlist active"

        if index >= len(self.playlist_audio_urls) or index < 0:
            log.inf("  [music] index out of range")
            return f"Error: index out of range. Index should be between 0 and {len(self.playlist_audio_urls)-1}"

        self.audio_index = index
        log.inf(f"  [music] playlist audio {self.audio_index+1}/{len(self.playlist_audio_urls)}")
        return self.play_audio(self.playlist_audio_urls[self.audio_index])

    def get_playlist_information(self):
        return self.audio_information

    def skip_audio(self, skip_count=1):
        if not self.is_playlist:
            log.inf("  [music] cannot move to next or previous audio: "
                    "no playlist active")
            return "Error: no playlist active"

        self.audio_index += skip_count
        return self.play_audio_at_playlist_index(self.audio_index)

    def pause(self):
        log.inf("  [music] pause player")
        was_playing = True
        try:
            was_playing = self.player.is_playing()
            self.player.pause()
            if was_playing and self.on_playback_stop:
                self.on_playback_stop()
            if not was_playing and self.on_playback_start:
                self.on_playback_start()
            act_str = "paused" if was_playing else "resumed"
            return {
                "result": "success",
                "state": f"playback {act_str}",
            }
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            act_str = "paused" if was_playing else "resumed"
            return {
                "result": "error",
                "state": f"playback pause could not be {act_str}",
                "reason": str(e),
            }

    def stop(self):
        log.inf("  [music] stop player and rewind to start")
        try:
            self.player.set_time(0)
            if self.player.is_playing():
                self.player.pause()
                if self.on_playback_stop:
                    self.on_playback_stop()
                return {
                    "result": "success",
                    "state": "playback stopped",
                }
            return {
                "result": "error",
                "state": "playback could not be stopped",
                "reason": "was not playing",
            }
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            return {
                "result": "error",
                "state": "playback could not be stopped",
                "reason": str(e),
            }

    def volume_up(self, increment=20):
        log.inf("  [music] volume up player")
        try:
            self.player.audio_set_volume(min(self.player.audio_get_volume() + increment, 100))
            return {
                "result": "success",
                "state": "volume up",
            }
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            return {
                "result": "error",
                "state": "volume could not be increased",
                "reason": str(e),
            }

    def volume_down(self, decrement=20):
        log.inf("  [music] volume down player")
        try:
            self.player.audio_set_volume(max(self.player.audio_get_volume() - decrement, 0))
            return {
                "result": "success",
                "state": "volume down",
            }
        except Exception as e:
            log.err(f"  [music] error: {str(e)}")
            return {
                "result": "error",
                "state": "volume could not be decreased",
                "reason": str(e),
            }

    def shutdown(self):
        if not self.player or not self.instance:
            return

        log.inf("  [music] shutdown")
        self.stop()

        # Release the media player instance
        log.inf("  [music] shutdown release player")
        self.player.release()
        self.player = None

        # Release the vlc instance
        log.inf("  [music] shutdown release vlc instance")
        self.instance.release()
        self.instance = None

    def __del__(self):
        self.shutdown()
