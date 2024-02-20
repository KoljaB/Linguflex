import base64
import requests
import cv2
import pyautogui
import os
from lingu import cfg


# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")
model = cfg("see", "model", default="gpt-4-vision-preview")

# Optimized prompt for additional clarity and detail
vision_prompt_text_simple = (
    "What’s in this image?"
)
vision_prompt_text_detailled = (
    "You are a highly knowledgeable scientific image analysis expert. "
    "Your task is to examine the following image in detail. "
    "Provide a comprehensive, factual, and scientifically accurate explanation of what the image depicts. "
    "Highlight key elements and their significance, and present your analysis in clear, well-structured markdown format. "
    "If applicable, include any relevant scientific terminology to enhance the explanation. "
    "Assume the reader has a basic understanding of scientific concepts."
    "Create a detailed image caption in bold explaining in short."
)
vision_prompt_text = (
    "You are a highly knowledgeable image analysis expert. "
    "Your task is to examine the following image in detail. "
    "Provide a comprehensive, factual, and accurate explanation of what the image depicts. "
    "Highlight key elements and their significance, and present a clear analysis. "
)
webcam_vision_prompt_text = (
    "You are a highly knowledgeable webcam image analysis expert. "
    "Your task is to examine the following webcam image in detail. "
    "Provide a comprehensive, factual, and accurate explanation of what the webcam image depicts. "
    "Highlight key elements and their significance, and present a clear analysis. "
)


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


def capture_webcam_image(output_file, width=640, height=480):
    """
    Captures a single high-resolution image from the webcam
    and saves it to the specified file.

    Args:
        output_file (str): The filename where the image will be saved.
        width (int, optional): Desired width of the image. Default is 1920.
        height (int, optional): Desired height of the image. Default is 1080.

    Raises:
        IOError: If the webcam cannot be opened or image cannot be captured.

    Returns:
        None
    """
    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Set the desired resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        cap.release()
        raise IOError("Cannot open webcam")

    # Capture a single frame
    ret, frame = cap.read()

    # Save the captured frame to a file
    if ret:
        cv2.imwrite(output_file, frame)
    else:
        cap.release()
        raise IOError("Cannot capture image from webcam")

    # Release the webcam
    cap.release()


def capture_screen_image(file_path):
    """
    Captures a screenshot of the entire screen
    and saves it to the specified file path.

    Args:
        file_path (str): The path where the screenshot will be saved.

    Returns:
        None
    """
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)


def get_image_analysis(image_path, prompt=webcam_vision_prompt_text):
    from openai import OpenAI
    client = OpenAI()

    base64_image = encode_image(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    params = {
        "model": model,
        # "temperature": self.temperature,
        "messages": messages,
        "stream": True,
        "max_tokens": 1000,
    }

    response = client.chat.completions.create(**params)

    analysis_content = ""
    print("Streaming response: ")
    for chunk in response:
        delta = chunk.choices[0].delta
        content = delta.content
        if content:
            print(content, end="", flush=True)
            analysis_content += content
    print("Streaming response finish")

    return analysis_content



# def get_image_analysis(image_path, prompt=webcam_vision_prompt_text):
#     """
#     Analyzes the image at the given path using OpenAI's API and
#     returns the analysis content.

#     Args:
#         image_path (str): The path to the image file.

#     Returns:
#         str: The content of the image analysis.
#     """
#     base64_image = encode_image(image_path)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }
#     payload = {
#         "model": "gpt-4-vision-preview",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": prompt
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         "max_tokens": 1000
#     }
#     # Send the API request
#     response = requests.post(
#         "https://api.openai.com/v1/chat/completions",
#         headers=headers,
#         json=payload
#     )

#     # Parse the response JSON and extract the analysis content
#     response_json = response.json()
#     analysis_content = (
#         response_json['choices'][0]['message']['content']
#         if response_json['choices']
#         else 'No analysis available.'
#     )

#     return analysis_content


# Example usage
# webcam_image_path = "webcam_image.jpg"
# capture_webcam_image(webcam_image_path)
# #capture_webcam_image(webcam_image_path, width=1920, height=1080)
# analysis = get_image_analysis(webcam_image_path)
# print(analysis)

# screenshot_path = "screenshot.jpg"
# capture_screen_image(screenshot_path)
# analysis = get_image_analysis(screenshot_path)
# print(analysis)