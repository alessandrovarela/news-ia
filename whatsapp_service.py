class WhatsAppService:
    def __init__(self, *, api_service):
        self.api_service = api_service
        print('----------------- API SERVICE --------------')
        print(api_service)

    def send_text_message_whasts_app(self, number, text, options=None):
        config = self.api_service.get_config()

        return self.api_service.send_text_message(config['instance_name'], number, text, options)
