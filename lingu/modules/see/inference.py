from lingu import Populatable, is_internal
from pydantic import BaseModel, Field
from .logic import logic
from typing import List


class LookAtWebcam(Populatable):
    """
    Call when you need to look at things or at the user.
    In many cases you should prefer to call this method over LookAtDesktop.
    Captures a single image from the webcam and submits it to the GPT Vision API,
    so you can see what's in front of the webcam.
    """

    def on_populated(self):
        return logic.capture_webcam()


class LookAtDesktop(Populatable):
    """
    Call ONLY when asked to look at the desktop.
    Check if it is better to call LookAtWebcam instead (in many cases it is).
    Captures a screenshot of the entire screen and submits it to the GPT Vision API,
    so you can see what is on the screen of the user.
    """

    def on_populated(self):
        return logic.capture_screen()
