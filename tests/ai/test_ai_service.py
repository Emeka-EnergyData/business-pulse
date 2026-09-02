from src.ai.ai_service import AIService
from src.ai.ollama_client import OllamaClient

def test_ai_service_generates_response():
    client = OllamaClient()
    service = AIService(client)
    
    response = service.generate_response("What are three things a small retail business should monitor every week")
    
    assert response
    assert isinstance(response,str)