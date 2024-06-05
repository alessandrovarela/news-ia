from groq import Groq

class GroqService:
    def __init__(self, base_url, api_key):
        self.client = Groq(api_key=api_key,)

    def make_request(self, messages, model, max_tokens):
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content