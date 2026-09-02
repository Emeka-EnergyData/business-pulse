from decimal import Decimal

from src.ai.insights import InsightsService


class FakeOllamaClient:
    def __init__(self):
        self.prompt = None
        self.system_prompt = None

    def generate(self, prompt, *, system_prompt=None):
        self.prompt = prompt
        self.system_prompt = system_prompt
        return "Test business insight"


def test_analyze_business_report():
    client = FakeOllamaClient()
    service = InsightsService(client)

    summary = {
        "number_of_sales": 20,
        "total_sales": Decimal("850000.00"),
        "total_paid": Decimal("640000.00"),
        "total_credit": Decimal("210000.00"),
        "collection_rate": 10,
        "credit_rate": 12,
        "number_of_purchases": 8,
        "total_purchases": Decimal("500000.00"),
    }

    result = service.analyze_business_report(summary)

    assert result == "Test business insight"
    assert "850,000.00" in client.prompt
    assert "210,000.00" in client.prompt
    assert client.system_prompt is not None