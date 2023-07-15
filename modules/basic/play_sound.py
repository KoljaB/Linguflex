import time
from core import BaseModule, Request, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR, play_sound, shutdown_sound

notice_message_seconds = int(cfg('notice_message_seconds', default=0))
notice_message_sound = cfg('notice_message_sound', default="notice")

class PlaySound(BaseModule):

    def init(self) -> None:
        play_sound("start_system")
        self.last_keepalive_time = time.time()

    def cycle(self, 
            request: Request) -> None: 
        """
        Check if the keepalive time has passed and play the audio if needed.
        """
        if notice_message_seconds > 0 and time.time() - self.last_keepalive_time >= notice_message_seconds:
            self.play()

    def play(self) -> None:
        self.last_keepalive_time = time.time()
        play_sound(notice_message_sound)

    def shutdown(self) -> None: 
        play_sound("shutdown")
        shutdown_sound()