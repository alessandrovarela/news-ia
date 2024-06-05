import json
from openai_service import OpenAIService
from groq_service import GroqService

class GenericAIService:
    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)
        self.openai_service = OpenAIService(config['OPENAI_API_KEY'], config['OPENAI_ORGANIZATION'], config['OPENAI_PROJECT'])
        self.groq_service = GroqService(config['GROQ_BASE_URL'], config['GROQ_API_KEY'])

    def generate_text(self, messages, ai, model, max_tokens=100):
        if ai == 'openai':
            return self.openai_service.make_request(messages, model, max_tokens)
        elif ai == 'groq':
            return self.groq_service.make_request(messages, model, max_tokens)
        else:
            raise ValueError(f"Unsupported AI: {ai}")