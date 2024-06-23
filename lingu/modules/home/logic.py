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

    def set_light_color(self, entity_id, color_name=None, hs_color=None, rgb_color=None):
        url = f"{self.base_url}/services/light/turn_on"
        payload = {"entity_id": entity_id}

        # Add color to the payload if provided
        if color_name:
            payload["color_name"] = color_name
        if hs_color:
            payload["hs_color"] = hs_color
        if rgb_color:
            payload["rgb_color"] = rgb_color

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return {"result": "success", "details": f"Color of light {entity_id} set successfully."}
        else:
            return {"result": "error", "details": response.text}


logic = HomeAssistantLogic()
