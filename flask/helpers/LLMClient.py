import openai
import requests
import json
from enum import Enum
from openai import OpenAI
import os

class LLMClientType(Enum):
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
class BaseClient:
    def generate_output(self, model, messages):
        raise NotImplementedError("Subclasses should implement this!")

class OpenAIClient(BaseClient):
    def __init__(self, api_key):
        os.environ['OPENAI_API_KEY'] = api_key
        self.client = OpenAI()

    def generate_output(self, model, messages):
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        output = completion.choices[0].message.content
        print(f"\n\nOUTPUT:\n{output}")
        return output

class HuggingFaceClient(BaseClient):
    def __init__(self, api_key):
        self.base_url = "https://api-inference.huggingface.co/v1/chat/completions"
        self.api_key = api_key

    def generate_output(self, model, messages):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "stream": True
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()  # Raise an error for bad responses

        output = ""
        for chunk in response.iter_lines():
            if chunk:
                chunk_data = chunk.decode('utf-8')
                if chunk_data.startswith('data:'):
                    chunk_json = chunk_data[5:]  # Remove 'data:'
                    if chunk_json:
                        try:
                            data = json.loads(chunk_json)
                            if 'choices' in data and len(data['choices']) > 0:
                                output += data['choices'][0]['delta']['content']
                        except json.JSONDecodeError:
                            continue  # Ignore any chunks that aren't valid JSON
        print(f"\n\nOUTPUT:\n{output}")
        return output

def generate_output_local(model, messages):
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def LLMGetClient(api_type: LLMClientType, api_key: str) -> BaseClient:
    if api_type == LLMClientType.OPENAI:
        return OpenAIClient(api_key)
    elif api_type == LLMClientType.HUGGINGFACE:
        return HuggingFaceClient(api_key)
    else:
        raise ValueError("Invalid API type specified.")
