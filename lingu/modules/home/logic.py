import requests
from lingu import Logic, log, cfg

bearer_token = cfg("home_assistant", "bearer_token")


class HomeAssistantLogic(Logic):
    base_url = "http://localhost:8123/api"
    headers = {
        "authorization": bearer_token,
        "content-type": "application/json"
    }

    # headers = {
    #     "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1YjgyOGNlYjgzMmQ0NTQyOWJjYWFkOWNjMGFhYWU4YyIsImlhdCI6MTcxOTA1NzA1NiwiZXhwIjoyMDM0NDE3MDU2fQ.ttg17ae_CXqWA_L7s_9AI1xDDStRYi52WmfbwmrufCI",
    #     "content-type": "application/json"
    # }

    def get_states(self):
        url = f"{self.base_url}/states"
        response = requests.get(url, headers=self.headers)
        log.dbg(f"Fetching states from Home Assistant")
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.json()}

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
