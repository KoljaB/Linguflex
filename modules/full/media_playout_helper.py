from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException
from datetime import datetime, timedelta

import urllib.parse
import threading
import time

YOUTUBE_URL = 'https://www.youtube.com/results?search_query='
TIME_SLEEP = 0.1


class YoutubeManagement():
    def __init__(self) -> None:
        self.driver = None
        self.running = True
        self.watch_ads = False
        self.watcher_active = False
        self.ad_playing = False
        self.desired_volume = 1
        self.last_mute = datetime.now()
        worker_thread = threading.Thread(target=self.ad_watcher)
        worker_thread.start()

    def ad_watcher(self)-> None:
        while self.running:
            if (self.watch_ads):
                try:
                    self.watcher_active = True
                    self.automute()
                    self.click('.ytp-ad-skip-button') # autoskip ads
                except InvalidSessionIdException as ex:
                    log(DEBUG_LEVEL_MAX, '  [playout] InvalidSessionIdException in ad_watcher, maybe user closed browser window?')
                    self.watch_ads = False
                    self.watcher_active = False
                    self.close()
                except Exception as ex:
                    log(DEBUG_LEVEL_MAX, '  [playout] Exception in ad_watcher, wtf happened here: '+ str(ex))
                    self.watch_ads = False
                    self.watcher_active = False
                    self.close()
            self.watcher_active = False
            time.sleep(TIME_SLEEP)

    def click(self, 
            element_name: str) -> None:
        elements = self.driver.find_elements(By.CSS_SELECTOR, element_name)
        if len(elements) > 0:
            try:
                wait = WebDriverWait(self.driver, 0.5)
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_name)))
                element.click()
            except TimeoutException:
                pass
            except Exception as ex:
                log(DEBUG_LEVEL_MAX, '  [playout] Exception in jv_youtube.py click: ' + str(ex))

    def volume(self, 
            volume: float) -> None:
        volume_string = "{:.2f}".format(volume)
        volume_string = volume_string.replace(",", ".")
        # Find the HTML5 video element
        video = self.driver.find_element(By.CSS_SELECTOR, "video")
        if video is not None:
            # Change the volume of the video
            js = self.driver.execute_script
            js(f"arguments[0].volume = {volume_string};", video)
        self.last_mute = datetime.now()

    # Mutes on non-skippable ads and unmutes when no ad
    def automute(self) -> None:
        ad1 = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-image-overlay")
        ad2 = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-text-overlay")
        ad3 = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-player-overlay")
        ad_playing = len(ad1) > 0 or len(ad2) > 0 or len(ad3) > 0
        ms_from_last_mute = (datetime.now() -  self.last_mute).microseconds
        # Set volume when ad playing state changes and additonally every 1 second
        if self.ad_playing != ad_playing or ms_from_last_mute > 1000:
            if ad_playing:
                self.volume(0)
            else:
                self.volume(self.desired_volume)
        self.ad_playing = ad_playing

    def open(self, 
            search_string: str) -> None:
        threading.Thread(target=self.open_async, args=(search_string,)).start()

    def open_async(self, 
            search_string: str) -> None:        
        try:
            self.close()
            encoded_string = urllib.parse.quote(search_string)
            url = YOUTUBE_URL + encoded_string

            log(DEBUG_LEVEL_MAX, '  [playout] starting firefox')
            self.driver = webdriver.Firefox()
            
            # Load the given URL
            log(DEBUG_LEVEL_MAX, '  [playout] opening ' + url)
            self.driver.get(url)
            
            WebDriverWait(self.driver, 3)
            time.sleep(0.5) # ? not sure if necessary
            # skip cookie ask window
            log(DEBUG_LEVEL_MAX, '  [playout] skip cookie window')
            actions = ActionChains(self.driver)
            for i in range(6):
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.1)
            actions.send_keys(Keys.ENTER).perform()
            WebDriverWait(self.driver, 3)
            time.sleep(3)
            # !!! suboptimal !!!  also returns childvideos from playlists besides main search result videos
            log(DEBUG_LEVEL_MAX, '  [playout] find search results')
            search_results = self.driver.find_elements(By.CSS_SELECTOR, '#video-title')
            # Find best search result
            log(DEBUG_LEVEL_MAX, '  [playout] calculating best search result')
            best_result = None
            max_matches = 0
            for search_result in search_results:
                s = search_result.text.lower()
                words = s.split()
                # Convert words into a set to remove duplicates 
                # Otherwise we'd count multiple occurrences of the same word within the search_result.text,
                # but actually want them to count only as one not prioritizing links that just repeat words
                unique_words = set(words)
                matches = sum(1 for word in unique_words if len(word) >= 4 and word in search_string.lower())
                matches -= 'live' in s  # Subtract 1 if "live" is in the string, 0 otherwise
                if matches > max_matches:
                    best_result = search_result
                    max_matches = matches
            if best_result is not None:
                log(DEBUG_LEVEL_MAX, '  [playout] opening best search result')
                best_result.click()
            else:
                return            
            self.watch_ads = True
        except Exception as ex:
            log(DEBUG_LEVEL_MAX, '  [playout] Exception in jv_youtube.py open: ' + str(ex))
            self.close()            

    def shutdown(self) -> None:
        self.running = False
        self.close()

    def close(self) -> None:
        log(DEBUG_LEVEL_MAX, '  [playout] closing running selenium firefox instances')
        self.watch_ads = False
        while self.watcher_active:
            time.sleep(0.1)
        if hasattr(self, 'driver') and self.driver is not None:
            self.driver.quit()
        log(DEBUG_LEVEL_MAX, '  [playout] all selenium firefox instances closed')