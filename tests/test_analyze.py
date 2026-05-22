import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

SAMPLE_METRICS = {
    "company_name": "Acme Corp",
    "revenue": 5000000,
    "burn_rate": 200000,
    "runway_months": 18,
    "ebitda_margin": -5.0,
    "gross_margin": 65.0,
    "revenue_growth_yoy": 120.0,
    "headcount": 42,
    "industry": "SaaS",
    "stage": "Series B",
}

MOCK_ANALYSIS = {
    "analysis": "Acme Corp shows strong top-line growth at 120% YoY...",
    "key_insights": ["Strong growth trajectory", "Negative EBITDA but improving margins"],
    "risk_flags": ["18-month runway requires near-term fundraise"],
    "recommendations": ["Accelerate path to profitability", "Optimize burn efficiency"],
}


@pytest.mark.asyncio
async def test_analyze_returns_200():
    with patch(
        "app.services.claude_client.analyze_financials",
        new=AsyncMock(return_value=MOCK_ANALYSIS),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/analyze", json={"metrics": SAMPLE_METRICS})

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Acme Corp"
    assert data["analysis"] == MOCK_ANALYSIS["analysis"]
    assert data["key_insights"] == MOCK_ANALYSIS["key_insights"]
    assert data["risk_flags"] == MOCK_ANALYSIS["risk_flags"]
    assert data["recommendations"] == MOCK_ANALYSIS["recommendations"]


@pytest.mark.asyncio
async def test_analyze_with_focus_areas():
    with patch(
        "app.services.claude_client.analyze_financials",
        new=AsyncMock(return_value=MOCK_ANALYSIS),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/analyze",
                json={"metrics": SAMPLE_METRICS, "focus_areas": ["liquidity", "growth"]},
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analyze_invalid_revenue():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        bad_metrics = {**SAMPLE_METRICS, "revenue": -1}
        response = await client.post("/analyze", json={"metrics": bad_metrics})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_missing_company_name():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        bad_metrics = {k: v for k, v in SAMPLE_METRICS.items() if k != "company_name"}
        response = await client.post("/analyze", json={"metrics": bad_metrics})

    assert response.status_code == 422
