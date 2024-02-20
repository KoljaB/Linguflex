import base64
import requests
import cv2
import pyautogui

# OpenAI API Key
api_key = "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"


def encode_image(image_path):
    """
    Encodes the image at the given path to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


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
    Captures a screenshot of the entire screen and saves it to the specified file path.

    Args:
        file_path (str): The path where the screenshot will be saved.

    Returns:
        None
    """
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)

def get_image_analysis(image_path):
    """
    Analyzes the image at the given path using OpenAI's API.

    Args:
        image_path (str): The path to the image file.

    Returns:
        None
    """
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What’s in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()


# Example usage
webcam_image_path = "webcam_image.jpg"
capture_webcam_image(webcam_image_path)
analyze_image(webcam_image_path)
