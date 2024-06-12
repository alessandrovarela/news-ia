import requests

class ZApiService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.z-api.io/instances/{instance_id}/{node_id}/"

    def authenticate(self, instance_id, node_id):
        self.base_url = self.base_url.format(instance_id=instance_id, node_id=node_id)

    def send_text_message(self, phone_number, message):
        url = self.base_url + "send-message-text"
        headers = {"X-API-KEY": self.api_key}
        data = {
            "phone": phone_number,
            "message": message
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()