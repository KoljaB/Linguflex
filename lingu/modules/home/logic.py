import requests
from lingu import Logic, log, cfg

home_assistant_url = cfg(
    "home_assistant",
    "url",
    default="homeassistant.local")
bearer_token = cfg(
    "home_assistant",
    "bearer_token")


class HomeAssistantLogic(Logic):

    base_url = f"http://{home_assistant_url}:8123/api"
    bearer_string = f"Bearer {bearer_token}"
    headers = {
        "authorization": bearer_string,
        "content-type": "application/json"
    }

    def get_states(self):
        url = f"{self.base_url}/states"
        print(f"Calling url {url} with headers {self.headers}")
        response = requests.get(url, headers=self.headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")  # Log the response text

        try:
            response_json = response.json()
            return {"result": "success", "details": response_json}
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {"result": "error", "details": response.text}  # Return the raw response text if JSON decoding fails

    # def turn_on_light(self, light_name):
    #     url = f"{self.base_url}/services/light/turn_on"
    #     payload = {"entity_id": f"light.{light_name}"}
    #     response = requests.post(url, headers=self.headers, json=payload)
    #     log.dbg(f"Turning on light '{light_name}' with payload: {payload}")
    #     if response.status_code == 200 or response.status_code == 201:
    #         return {"result": "success", "details": response.json()}
    #     else:
    #         return {"result": "error", "details": response.json()}

    # def turn_off_light(self, light_name):
    #     url = f"{self.base_url}/services/light/turn_off"
    #     payload = {"entity_id": f"light.{light_name}"}
    #     response = requests.post(url, headers=self.headers, json=payload)
    #     log.dbg(f"Turning off light '{light_name}' with payload: {payload}")
    #     if response.status_code == 200 or response.status_code == 201:
    #         return {"result": "success", "details": response.json()}
    #     else:
    #         return {"result": "error", "details": response.json()}

    # def set_light_color(self, light_name, color):
    #     # Convert hex color to RGB
    #     color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    #     url = f"{self.base_url}/services/light/turn_on"
    #     payload = {
    #         "entity_id": f"light.{light_name}",
    #         "rgb_color": color_rgb
    #     }
    #     response = requests.post(url, headers=self.headers, json=payload)
    #     log.dbg(f"Setting light '{light_name}' to color '{color}' (RGB: {color_rgb}) with payload: {payload}")
    #     if response.status_code == 200 or response.status_code == 201:
    #         return {"result": "success", "details": response.json()}
    #     else:
    #         return {"result": "error", "details": response.json()}


logic = HomeAssistantLogic()
