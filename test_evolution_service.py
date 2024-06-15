import unittest
import requests
import json

class TestEvolutionApiService(unittest.TestCase):
    def setUp(self):
        with open('config.json') as f:
            config = json.load(f)
        whatsapp_config = config['whatsapp']['api_service']
        self.server_url = whatsapp_config['server_url']
        self.api_key = whatsapp_config['api_key']
        self.instance_name = whatsapp_config['instance_name']

    def test_send_message(self):
        url = f"{self.server_url}/message/sendText/{self.instance_name}"
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        data = {
            "number": "15142612760",
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": "Test message"
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)

    def test_send_media_url_message(self):
        url = f"{self.server_url}/message/sendMedia/{self.instance_name}"
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        data = {
            "number": "15142612760",
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "mediaMessage": {
                "mediatype": "image",
                "caption": "This is an example JPG image file sent by Evolution-API via URL.",
                "media": "https://evolution-api.com/files/evolution-api.jpg"
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()