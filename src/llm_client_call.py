import os
from dotenv import load_dotenv  # type: ignore 
from huggingface_hub import InferenceClient # type: ignore

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_ID = os.getenv("HF_MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct")


class LLMClient:
    """
    Lightweight LLM client wrapper. Does not raise on import if API key is missing.
    Use `is_configured()` to check availability before calling `call()`.
    """
    def __init__(self):
        self.api_key = HF_API_KEY
        self.client = None
        if self.api_key:
            self.client = InferenceClient(api_key=self.api_key)

    def is_configured(self) -> bool:
        return self.client is not None

    def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make a real LLM call using Hugging Face chat completion.
        Raises a RuntimeError if HF_API_KEY is not configured.
        Returns ONLY model-generated text.
        """
        if not self.is_configured():
            raise RuntimeError(
                "HF_API_KEY not found."
            )

        messages = [
            # system prompt for instructing the model and user prompt for getting response
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
        )

        return response.choices[0].message.content
