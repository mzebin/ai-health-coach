import requests


class OllamaClient:
    def __init__(self, model="llama3.2:latest", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt, context=None, max_tokens=150):
        """Send a prompt to Ollama and return a concise response."""
        # Build the prompt with context if provided
        if context:
            full_prompt = f"Context: {context}\n\nUser: {prompt}\nAssistant:"
        else:
            full_prompt = f"User: {prompt}\nAssistant:"

        # System instruction for brevity
        system_instruction = (
            "You are a helpful AI health coach. Keep your answers brief and to the point "
            "(under 100 words). Do not include extra commentary unless asked."
        )

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "system": system_instruction,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "Sorry, I couldn't generate a response.")
        except Exception as e:
            return f"Error communicating with LLM: {e}"