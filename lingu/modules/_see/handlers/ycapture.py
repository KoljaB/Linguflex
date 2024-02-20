import base64
import requests
import imageio
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
    # Replace '<video0>' with the correct identifier or index for your webcam.
    # Often, the first webcam can be accessed with '0'.
    try:
        reader = imageio.get_reader(0)
        frame = reader.get_data(0)
        imageio.imwrite(output_file, frame)
        reader.close()
    except Exception as e:
        print(f"Error capturing webcam image: {e}")

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

def analyze_image(image_path):
    """
    Analyzes the image at the given path using OpenAI's API and prints the response.

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
    print(response.json())


# Example usage
webcam_image_path = "webcam_image.jpg"
capture_webcam_image(webcam_image_path)
#analyze_image(webcam_image_path)
