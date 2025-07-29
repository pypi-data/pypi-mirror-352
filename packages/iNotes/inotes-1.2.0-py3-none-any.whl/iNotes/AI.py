import requests
import json

models = {
    "neversleep/llama-3-lumimaid-8b:extended", "anthropic/claude-3-7-sonnet-20250219",
    "sao10k/l3-euryale-70b", "deepseek/deepseek-chat", "deepseek/deepseek-r1",
    "openai/gpt-4o-mini", "gryphe/mythomax-l2-13b", "google/gemini-pro-1.5",
    "x-ai/grok-2", "nvidia/llama-3.1-nemotron-70b-instruct"
}

class iNotes:
    def __init__(self, api_url="https://netwrck.com/api/chatpred_or", 
                 model="deepseek/deepseek-r1", 
                 system_prompt="You are an AI notes maker which makes notes on the basis of given prompt. Keep Headings and subheadings bold and stylish.", 
                 ):  
        self.api_url = api_url
        self.model = model
        self.system_prompt = system_prompt
        self.headers = {
            "content-type": "application/json",
            "origin": "https://netwrck.com"
        }

    def send_request(self, prompt):
        if self.model not in models:
            return f"Error: Model '{self.model}' is not supported. Choose from {models}"

        payload = {
            "model_name": self.model,
            "context": self.system_prompt,
            "query": prompt
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)

            if response.status_code == 200:
                    try:
                        # Attempt to parse the response as JSON
                        response_data = response.json()
                        if isinstance(response_data, dict):  # Ensure it's a dictionary
                            return response_data.get("content", "")
                        else:
                            # If it's not a dictionary, treat it as raw text
                            return response.text
                    except json.JSONDecodeError:
                        # If the response is not JSON, return it as plain string
                        return response.text
            else:
                return f"Error: {response.status_code}, {response.text}"

        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"