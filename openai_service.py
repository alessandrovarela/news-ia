from openai import OpenAI

class OpenAIService:
    def __init__(self, api_key, organization, project):
        self.client = OpenAI(api_key=api_key, organization=organization, project=project)

    def make_request(self, messages, model, max_tokens):
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content