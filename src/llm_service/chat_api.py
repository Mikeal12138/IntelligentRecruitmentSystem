import os
from openai import OpenAI


class LLMChatAPI:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    def chat(self, messages: list) -> str:
        pass
    
    def complete(self, prompt: str) -> str:
        pass
