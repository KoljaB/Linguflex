import json
import requests
from lingu import Logic, log, cfg

home_assistant_url = cfg(
    "home_assistant",
    "url",
    default="homeassistant.local")
bearer_token = cfg(
    "home_assistant",
    "bearer_token")
entity_whitelist_str = cfg(
    "home_assistant",
    "entity_whitelist",
    default="switch.,light.,sensor.")
entity_whitelist = entity_whitelist_str.split(',')
entity_blacklist_str = cfg(
    "home_assistant",
    "entity_blacklist",
    default="_kindersicherung,_parental")
entity_blacklist = entity_blacklist_str.split(',')
attribute_map = cfg(
    "home_assistant",
    "attribute_map",
    default={
        'light': ['brightness', 'color_mode', 'supported_color_modes', 'color_temp', 'hs_color'],
        'switch': []
    })


class HomeAssistantLogic(Logic):

    base_url = f"http://{home_assistant_url}:8123/api"
    bearer_string = f"Bearer {bearer_token}"
    headers = {
        "authorization": bearer_string,
        "content-type": "application/json"
    }

    # Function to check if entity is allowed
    def is_entity_allowed(self, entity_id):
        # Check blacklist
        if any(blacklist in entity_id for blacklist in entity_blacklist):
            return False

        # Check whitelist
        if any(whitelist in entity_id for whitelist in entity_whitelist):
            return True

        return False

    def extract_relevant_info(self, data):
        relevant_info = []

        for entity in data:
            entity_id = entity.get('entity_id')
            if not self.is_entity_allowed(entity_id):
                continue

            # Basic entity information
            entity_info = {
                'entity_id': entity_id,
                'friendly_name': entity.get('attributes', {}).get('friendly_name', 'Unknown'),
                'state': entity.get('state', 'Unknown')
            }

            # Process entity-specific attributes based on the attribute map
            attributes = entity.get('attributes', {})
            if attributes:
                for entity_type, attr_list in attribute_map.items():
                    if entity_type in entity_id:
                        # Extract and clean specific attributes for this entity type
                        specific_attributes = {attr: attributes.get(attr) for attr in attr_list if attr in attributes}
                        specific_attributes = {k: v for k, v in specific_attributes.items() if v is not None}
                        entity_info.update(specific_attributes)

            # Append the cleaned and processed entity information
            relevant_info.append(entity_info)

        return relevant_info

    def get_states(self):
        url = f"{self.base_url}/states"
        response = requests.get(url, headers=self.headers)

        try:
            response_json = response.json()
            relevant_info = self.extract_relevant_info(response_json)
            return {"result": "success", "details": relevant_info}
        except requests.exceptions.JSONDecodeError as e:
            return {"result": "error", "details": response.text}  # Return the raw response text if JSON decoding fails

    def turn_on_light(self, entity_id):
        url = f"{self.base_url}/services/light/turn_on"
        payload = {"entity_id": entity_id}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Light {entity_id} turned on successfully."}
        else:
            return {"result": "error", "details": response.text}

    def turn_off_light(self, entity_id):
        url = f"{self.base_url}/services/light/turn_off"
        payload = {"entity_id": entity_id}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Light {entity_id} turned off successfully."}
        else:
            return {"result": "error", "details": response.text}

    def turn_on_switch(self, entity_id):
        url = f"{self.base_url}/services/switch/turn_on"
        payload = {"entity_id": entity_id}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Switch {entity_id} turned on successfully."}
        else:
            return {"result": "error", "details": response.text}

    def turn_off_switch(self, entity_id):
        url = f"{self.base_url}/services/switch/turn_off"
        payload = {"entity_id": entity_id}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Switch {entity_id} turned off successfully."}
        else:
            return {"result": "error", "details": response.text}

    def set_light_color(
            self,
            entity_id,
            color_name=None,
            # hs_color=None,
            rgb_color=None):
        url = f"{self.base_url}/services/light/turn_on"
        payload = {"entity_id": entity_id}

        # Add color to the payload if provided
        if color_name:
            payload["color_name"] = color_name
        # elif hs_color:
            # payload["hs_color"] = hs_color
        elif rgb_color:
            payload["rgb_color"] = rgb_color

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Color of light {entity_id} set successfully."}
        else:
            return {"result": "error", "details": response.text}

    def set_temperature(self, entity_id, temperature):
        url = f"{self.base_url}/services/climate/set_temperature"
        payload = {"entity_id": entity_id, "temperature": temperature}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": f"Temperature for {entity_id} set to {temperature} successfully."}
        else:
            return {"result": "error", "details": response.text}

    def lock(self, entity_id):
        url = f"{self.base_url}/services/lock/lock"
        payload = {"entity_id": entity_id}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": f"Lock {entity_id} locked successfully."}
        else:
            return {"result": "error", "details": response.text}

    def unlock(self, entity_id):
        url = f"{self.base_url}/services/lock/unlock"
        payload = {"entity_id": entity_id}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": f"Lock {entity_id} unlocked successfully."}
        else:
            return {"result": "error", "details": response.text}

    def get_config(self):
        url = f"{self.base_url}/config"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def get_events(self):
        url = f"{self.base_url}/events"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def get_services(self):
        url = f"{self.base_url}/services"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def get_history(self, start_time=None, end_time=None, filter_entity_id=None):
        url = f"{self.base_url}/history/period"
        params = {}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if filter_entity_id:
            params['filter_entity_id'] = filter_entity_id
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def get_logbook(self, start_time=None, end_time=None, entity=None):
        url = f"{self.base_url}/logbook"
        params = {}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if entity:
            params['entity'] = entity
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    # def get_camera_image(self, entity_id):
    #     url = f"{self.base_url}/camera_proxy/{entity_id}"
    #     response = requests.get(url, headers=self.headers)
    #     if response.status_code == 200:
    #         return {"result": "success", "details": response.content}
    #     else:
    #         return {"result": "error", "details": response.text}

    def get_calendars(self):
        url = f"{self.base_url}/calendars"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def get_calendar_events(self, calendar_entity_id, start, end):
        url = f"{self.base_url}/calendars/{calendar_entity_id}"
        params = {'start': start, 'end': end}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def update_state(self, entity_id, state, attributes=None):
        url = f"{self.base_url}/states/{entity_id}"
        payload = {"state": state}
        if attributes:
            payload["attributes"] = attributes
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code in [200, 201]:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def fire_event(self, event_type, event_data=None):
        url = f"{self.base_url}/events/{event_type}"
        payload = event_data if event_data else {}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def call_service(self, domain, service, service_data=None):
        url = f"{self.base_url}/services/{domain}/{service}"
        payload = service_data if service_data else {}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def render_template(self, template):
        url = f"{self.base_url}/template"
        payload = {"template": template}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": response.text}
        else:
            return {"result": "error", "details": response.text}

    def check_config(self):
        url = f"{self.base_url}/config/core/check_config"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

    def handle_intent(self, name, data):
        url = f"{self.base_url}/intent/handle"
        payload = {"name": name, "data": data}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return {"result": "success", "details": response.json()}
        else:
            return {"result": "error", "details": response.text}

logic = HomeAssistantLogic()
