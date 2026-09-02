from src.ai.ollama_client import OllamaClient
from src.ai.prompts import(BUSINESS_REPORT_SYSTEM_PROMPT, build_business_report_prompt)


class InsightsService:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        
    def analyze_business_report(self, summary:dict)-> str:
        """
        Analyze a Business Pulse business summary and return AI-generated insights.
        """
        
        prompt = build_business_report_prompt(summary)
        
        return self.ollama_client.generate(prompt, system_prompt=BUSINESS_REPORT_SYSTEM_PROMPT)