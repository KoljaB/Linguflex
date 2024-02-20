from .handlers.capture import (
    capture_webcam_image,
    capture_screen_image,
    get_image_analysis
)
from lingu import cfg, Logic


img_width = int(cfg("see", "img_width", default=640))
img_height = int(cfg("see", "img_height", default=480))
output_file_webcam = cfg("see", "output_file_webcam", default="webcam.jpg")
output_file_screen = cfg("see", "output_file_screenshot", default="screen.jpg")


class SeeLogic(Logic):
    def __init__(self):
        super().__init__()
        self.image_to_process = None

    def capture_webcam(self, output_file=output_file_webcam):
        capture_webcam_image(output_file, img_width, img_height)
        self.image_to_process = output_file
        return self.image_to_process
        # analysis = get_image_analysis(output_file)
        # return analysis

    def capture_screen(self, output_file=output_file_screen):
        capture_screen_image(output_file)
        self.image_to_process = output_file
        return self.image_to_process
        # analysis = get_image_analysis(output_file)
        # return analysis


logic = SeeLogic()
