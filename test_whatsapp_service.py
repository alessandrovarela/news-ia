import unittest
import json
from whatsapp_service import WhatsAppService
from evolution_service import EvolutionApiService # noqa: F401

class TestWhatsAppService(unittest.TestCase):
    def setUp(self):
        # Load the configuration for the WhatsApp API service
        with open("config.json") as config_file:
            config = json.load(config_file)

        whatsapp_api_config = config["whatsapp"]["api_service"]
        service_class_name = whatsapp_api_config.pop("service_class_name", None)
        # instance_name = whatsapp_api_config.pop("instance_name", None)
        service_class = globals()[service_class_name]

        whatsapp_api_service = service_class(whatsapp_api_config)
        #whatsapp_api_service.instance_name = instance_name

        # Create an instance of WhatsAppService
        self.whatsapp_service = WhatsAppService(api_service=whatsapp_api_service)

    def test_send_text_message(self):
        number = '15142612760'
        text = 'Hello, world!'
        options = None
        response_body, status_code = self.whatsapp_service.send_text_message_whatsapp(number, text, options)
        if status_code != 201:
            print('----------------- RESPOSTA --------------')
            print(response_body)
            self.fail(f"Expected status code 201, got {status_code}")
        else:
            self.assertEqual(status_code, 201, f"Expected status code 201, got {status_code}")

    def test_send_media_url_message(self):
        number = '15142612760'
        media_url = 'https://evolution-api.com/files/evolution-api.jpg'
        caption = 'This is a test image'
        options = None
        response_body, status_code = self.whatsapp_service.send_media_url_whatsapp(number, media_url, caption, options)
        if status_code != 201:
            print('----------------- RESPOSTA --------------')
            print(response_body)
            self.fail(f"Expected status code 201, got {status_code}")
        else:
            self.assertEqual(status_code, 201, f"Expected status code 201, got {status_code}")
if __name__ == '__main__':
    unittest.main()