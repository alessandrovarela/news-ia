class WhatsAppService:
    def __init__(self, *, api_service):
        self.api_service = api_service
        
    def send_text_message_whatsapp(self, number, text):
        return self.api_service.send_text_message(number, text)

    def send_media_url_whatsapp(self, number, media_url, caption=""):
        return self.api_service.send_media_url_message(number=number, media_url=media_url, caption=caption)