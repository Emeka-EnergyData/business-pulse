from datetime import date
from decimal import Decimal

import pytest

from src.ai.insights import InsightsService
from src.ai.ollama_client import OllamaClient


@pytest.mark.integration
def test_business_report_ai_analysis():
    ollama_client = OllamaClient()
    insights_service = InsightsService(ollama_client)

    summary = {
        "number_of_sales": 42,
        "total_sales": Decimal("850000.00"),
        "total_paid": Decimal("640000.00"),
        "total_credit": Decimal("210000.00"),
        "collection_rate": 10,
        "credit_rate": 10,
        "number_of_purchases": 12,
        "total_purchases": Decimal("500000.00"),
    }

    result = insights_service.analyze_business_report(summary)

    assert result
    assert isinstance(result, str)
    assert len(result.strip()) > 0