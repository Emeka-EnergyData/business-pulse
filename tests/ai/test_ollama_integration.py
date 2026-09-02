import pytest

from src.ai.ollama_client import OllamaClient


@pytest.mark.integration
def test_ollama_generate():
    client = OllamaClient()

    if not client.health_check():
        pytest.skip("Ollama is not running.")

    response = client.generate(
        "Say exactly: Business Pulse AI test successful."
    )

    assert response
    assert "Business Pulse" in response