import requests
import random

class EvolutionApiService:
    def __init__(self, config):
        self._config = config

    def send_text_message(self, instance, number, text, options=None):
        url = f"https://{self._config['server_url']}/message/sendText/{instance}"

        # Calculate the delay if delay_enabled is True
        delay = self.calculate_delay(text, self._config['average_char_min']) if self._config.get('delay_enabled', False) else 0

        headers = {
            "apikey": self._config['api_key'],
            "Content-Type": "application/json"
        }
        payload = {
            "number": number,
            "options": {"delay": delay} if options is None else options,
            "textMessage": {"text": text}
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def calculate_delay(self, message, average_char_min):
        # Calculate the number of characters per second
        chars_per_second = average_char_min / 60

        # Calculate the delay in seconds
        delay_seconds = len(message) / chars_per_second

        # Randomize the delay by up to 30%
        random_factor = random.uniform(0.7, 1.3)
        delay_seconds *= random_factor

        # Convert the delay to milliseconds
        delay_milliseconds = delay_seconds * 1000

        return delay_milliseconds