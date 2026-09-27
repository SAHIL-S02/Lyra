import os

from dotenv import load_dotenv
from google import genai

from .base import AIProvider


load_dotenv()


class GeminiProvider(AIProvider):
    """Gemini implementation of Lyra's generic AI provider."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the environment."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.7-flash"

    async def respond(self, text: str) -> str:
        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=text,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text