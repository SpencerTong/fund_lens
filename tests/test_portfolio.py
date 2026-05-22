import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app

COMPANY_A = {
    "company_name": "GrowthCo",
    "revenue": 8000000,
    "ebitda_margin": 12.0,
    "gross_margin": 72.0,
    "revenue_growth_yoy": 85.0,
    "runway_months": 24,
    "industry": "SaaS",
    "stage": "Series B",
}

COMPANY_B = {
    "company_name": "StableCo",
    "revenue": 15000000,
    "ebitda_margin": 22.0,
    "gross_margin": 68.0,
    "revenue_growth_yoy": 30.0,
    "runway_months": None,
    "industry": "SaaS",
    "stage": "Series C",
}

MOCK_COMPARISON = {
    "comparison": "GrowthCo is growing faster while StableCo has superior profitability...",
    "winner_by_category": {
        "growth": "GrowthCo",
        "profitability": "StableCo",
        "efficiency": "StableCo",
        "financial_health": "StableCo",
    },
    "summary": "StableCo is better positioned overall given its profitability and scale.",
}


@pytest.mark.asyncio
async def test_compare_returns_200():
    with patch(
        "app.services.claude_client.compare_companies",
        new=AsyncMock(return_value=MOCK_COMPARISON),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/portfolio/compare",
                json={"company_a": COMPANY_A, "company_b": COMPANY_B},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["company_a_name"] == "GrowthCo"
    assert data["company_b_name"] == "StableCo"
    assert data["comparison"] == MOCK_COMPARISON["comparison"]
    assert data["winner_by_category"]["growth"] == "GrowthCo"
    assert data["summary"] == MOCK_COMPARISON["summary"]


@pytest.mark.asyncio
async def test_compare_with_criteria():
    with patch(
        "app.services.claude_client.compare_companies",
        new=AsyncMock(return_value=MOCK_COMPARISON),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/portfolio/compare",
                json={
                    "company_a": COMPANY_A,
                    "company_b": COMPANY_B,
                    "comparison_criteria": ["growth", "profitability"],
                },
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_compare_missing_company_b():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/portfolio/compare", json={"company_a": COMPANY_A}
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
