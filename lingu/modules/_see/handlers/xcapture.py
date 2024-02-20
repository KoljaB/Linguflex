import cv2
import pyautogui


def capture_webcam_image(output_file):
    """
    Captures a single image from the webcam and saves it to the specified file.

    Args:
    output_file (str): The filename where the image will be saved.

    Returns:
    None
    """
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    # Capture a single frame
    ret, frame = cap.read()

    # Save the captured frame to a file
    if ret:
        cv2.imwrite(output_file, frame)
    else:
        raise IOError("Cannot capture image from webcam")

    # Release the webcam
    cap.release()


def capture_screen_image(file_path):
    """
    Captures a screenshot of the entire screen
    and saves it to the specified file path.

    Args:
    file_path (str): The path where the screenshot will be saved,
      including the file name and extension.

    Returns:
    None
    """
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)

# capture_webcam_image('webcam_image.jpg')
# capture_screen_image('screenshot.png')
