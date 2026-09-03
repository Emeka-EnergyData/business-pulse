import os

from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.7-flash",
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        """Send a prompt to Gemini and return the generated response."""

        contents = prompt

        if system_prompt:
            contents = (
                f"System instructions:\n{system_prompt}\n\n"
                f"User request:\n{prompt}"
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()