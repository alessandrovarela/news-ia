import requests
import random

class EvolutionApiService:
    def __init__(self, config):
        self._config = config

    def get_config(self):
        return self._config        

    def send_text_message(self, number, text, options=None):
        url = f"{self._config.get('server_url')}/message/sendText/{self._config.get('instance_name')}"

        delay = self.calculate_delay(text)

        headers = {
            "apikey": self._config['api_key'],
            "Content-Type": "application/json"
        }
        payload = {
            "number": number,
            "options": {"delay": delay} if options is None else options,
            "textMessage": {"text": text}
        }

        print( '----------------- PAYLOAD ------------')
        print(payload)
        response = requests.post(url, json=payload, headers=headers)
        return (response.json(), response.status_code)

    def send_media_url_message(self, number, media_url, caption, options=None):
        url = f"{self._config.get('server_url')}/message/sendMedia/{self._config.get('instance_name')}"

        delay = self.calculate_delay(caption)
        if options is None:
            options = {"delay": delay, "presence": "composing"}

        headers = {
            "apikey": self._config['api_key'],
            "Content-Type": "application/json"
        }
        payload = {
            "number": number,
            "options": options,
            "mediaMessage": {
                "mediatype": "image",
                "caption": caption,
                "media": media_url
            }
        }

        print('----------------- PAYLOAD ------------')
        print(payload)
        response = requests.post(url, json=payload, headers=headers)
        return (response.json(), response.status_code)

    def calculate_delay(self, message):

        if self._config.get('delay_by_size_message', False):
            seconds_per_char =  60 / self._config.get['average_char_min']
            delay_seconds = len(message) / seconds_per_char            
            delay_milliseconds = delay_seconds * 1000
        else:
            delay_milliseconds = self._config.get('delay_default_ms', 1200)
        
        # Randomize the delay by up to 30%
        random_factor = random.uniform(0.7, 1.3)
        delay_milliseconds *= random_factor

        return int(delay_milliseconds)
    