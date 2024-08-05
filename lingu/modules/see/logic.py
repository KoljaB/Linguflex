from .handlers.capture import (
    capture_webcam_image,
    capture_screen_image,
)
from lingu import cfg, Logic


img_width = int(cfg("see", "img_width", default=640))
img_height = int(cfg("see", "img_height", default=480))
output_file_webcam = cfg("see", "output_file_webcam", default="webcam.jpg")
output_file_screen = cfg("see", "output_file_screenshot", default="screen.jpg")


class SeeLogic(Logic):
    """Logic for capturing and processing images from webcam and screen.

    Attributes:
        img_width (int): Width of the image to capture.
        img_height (int): Height of the image to capture.
        output_file_webcam (str): Default path for webcam image.
        output_file_screen (str): Default path for screen capture.
        image_to_process (str): Path of the last captured image.
    """

    def __init__(self):
        """Initializes SeeLogic with configuration values."""
        super().__init__()
        self.img_width = int(cfg("see", "img_width", default=640))
        self.img_height = int(cfg("see", "img_height", default=480))
        self.output_file_webcam = cfg(
            "see",
            "output_file_webcam",
            default="webcam.jpg")
        self.output_file_screen = cfg(
            "see",
            "output_file_screenshot",
            default="screen.jpg")
        self.image_to_process = None
        self.image_source = None

    def capture_webcam(self, output_file=None):
        """Captures image from the webcam.

        Args:
            output_file (str, optional): File path to save the image.
              Defaults to self.output_file_webcam.

        Returns:
            str: Path of the captured image.
        """
        output_file = output_file or self.output_file_webcam
        capture_webcam_image(output_file, self.img_width, self.img_height)
        self.image_to_process = output_file
        self.image_source = "webcam"
        return self.image_to_process

    def capture_screen(self, output_file=None):
        """Captures screenshot.

        Args:
            output_file (str, optional): File path to save the screenshot.
              Defaults to self.output_file_screen.

        Returns:
            str: Path of the captured screenshot.
        """
        output_file = output_file or self.output_file_screen
        capture_screen_image(output_file)
        self.image_to_process = output_file
        self.image_source = "screen"
        return self.image_to_process


logic = SeeLogic()
