import requests


class OllamaClient:
    def __init__(self, model="llama3.2:latest", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, query, history=None, context=None, max_tokens=300):
        """
        Generate a response with optional conversation history and context.

        Args:
            query: Current user query.
            history: List of (role, message) tuples (role = 'user' or 'assistant').
            context: Additional context (e.g., latest metrics).
            max_tokens: Maximum tokens in response.
        """
        # Build conversation from history
        conversation = ""
        if history:
            # Take last 5 exchanges (10 entries) to avoid token limits
            recent = history[-10:] if len(history) > 10 else history
            for role, msg in recent:
                prefix = "User" if role == "user" else "Assistant"
                conversation += f"{prefix}: {msg}\n"
        # Add current query
        conversation += f"User: {query}\nAssistant:"

        # Prep context if provided
        full_prompt = conversation
        if context:
            full_prompt = f"Context: {context}\n\n{conversation}"

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
