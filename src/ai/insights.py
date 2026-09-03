from src.ai.gemini_client import GeminiClient
from src.ai.prompts import(BUSINESS_REPORT_SYSTEM_PROMPT, build_business_report_prompt)


class InsightsService:
    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        
    def analyze_business_report(self, summary:dict)-> str:
        """
        Analyze a Business Pulse business summary and return AI-generated insights.
        """
        
        prompt = build_business_report_prompt(summary)
        
        return self.gemini_client.generate(prompt, system_prompt=BUSINESS_REPORT_SYSTEM_PROMPT)