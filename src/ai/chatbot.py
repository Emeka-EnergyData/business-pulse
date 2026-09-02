from src.ai.ollama_client import OllamaClient
from src.ai.prompts import (BUSINESS_CHAT_SYSTEM_PROMPT, build_business_chat_prompt)


class BusinessChatService:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client

    def ask(
        self,
        summary: dict,
        user_question: str
    ) -> str:
        """
        Answer a user's question about a Business Pulse report.
        """

        prompt = build_business_chat_prompt(
            summary,
            user_question
        )

        return self.ollama_client.generate(
            prompt,
            system_prompt=BUSINESS_CHAT_SYSTEM_PROMPT
        )