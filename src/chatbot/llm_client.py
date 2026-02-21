import requests


class OllamaClient:
    def __init__(self, model="llama3.2:latest", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, query, history=None, context=None, max_tokens=300):
        """
        Generate a response with strict instructions.
        - history: list of (role, message) tuples (user/assistant)
        - context: optional extra context (e.g., latest metrics)
        """
        # System instruction to enforce topic boundaries
        system = (
            "You are a helpful AI health coach. You have access to the user's conversation history as context, "
            "but your task is to answer only the user's latest question. "
            "If the latest question is about health, fitness, wellness, nutrition, or related to the user's personal health data, "
            "provide a concise answer. "
            "If the question is off-topic (e.g., weather, news, politics, general knowledge, personal questions about yourself), "
            "respond with exactly: 'I'm not sure how to answer that.' without any additional commentary. "
            "Do not reference the conversation history unless it directly helps answer the current question about health. "
            "Keep answers concise and focused on the question."
        )

        # Build conversation with clear separation
        conversation = ""
        if history:
            # Show last 5 exchanges (10 lines) as context
            recent = history[-10:] if len(history) > 10 else history
            for role, msg in recent:
                prefix = "User" if role == "user" else "Assistant"
                conversation += f"{prefix}: {msg}\n"
        else:
            conversation = "No previous conversation.\n"

        # Add current query explicitly
        conversation += f"Current user query: {query}\nAssistant:"

        # Prepend any additional context (like latest metrics)
        if context:
            conversation = f"Context: {context}\n\n{conversation}"

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": conversation,
            "system": system,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "stop": ["\nUser:", "\nAssistant:", "\nCurrent user query:"]
            }
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "Sorry, I couldn't generate a response.").strip()
        except Exception as e:
            return f"Error communicating with LLM: {e}"