import json
import os
from urllib import request
from urllib.error import URLError, HTTPError

class OllamaClient:
    def __init__(self, 
                 base_url:str | None = None,
                 model:str | None = None,
                 timeout: int = 1200
                 ):
        self.base_url = (base_url 
                         or os.getenv("OLLAMA_BASE_URL") 
                         or "http://localhost:11434").rstrip("/")
        self.model = (model 
                      or os.getenv("OLLAMA_MODEL")
                      or "llama3.2:1b")
        self.timeout = timeout
        
    def generate(
        self,
        prompt:str,
        *,
        system_prompt: str | None = None
    ) -> str:
        """Send a prompt to Ollama and return the generated response"""
        payload = {
            "model":self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        data = json.dumps(payload).encode("utf-8")
        
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={
                "Content-Type":"application/json"
            },
            method="POST"
        )
        
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                
        except HTTPError as exc:
            raise RuntimeError(f"Could not connect to Ollama at {self.base_url}: {exc.reason}") from exc
        
        response_text = result.get("response")
        
        if not response_text:
            raise RuntimeError("Ollama returned an empty response.")
        
        return response_text.strip()
    
    def health_check(self) -> bool:
        """Check whether Ollama is reachable."""
   
        req= request.Request(f"{self.base_url}/api/tags", method="GET")
        
        try:
            with request.urlopen(req,timeout=10):
                return True
        except (HTTPError, URLError, TimeoutError):
            return False