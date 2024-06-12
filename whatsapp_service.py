class WhatsAppService:
    def __init__(self, *, api_service):
        self.api_service = api_service

    def send_text_message(self, number, text, options=None):
        return self.api_service.send_text_message(number, text, options)