import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.conversation import Message

MOCK_ANSWER = "Based on your burn rate and runway, I recommend targeting a Series B raise within 9 months."
MOCK_HISTORY = [
    Message(role="user", content="What should I prioritize?"),
    Message(role="assistant", content=MOCK_ANSWER),
]


@pytest.mark.asyncio
async def test_ask_basic_question():
    with patch(
        "app.services.claude_client.chat",
        new=AsyncMock(return_value=(MOCK_ANSWER, MOCK_HISTORY)),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/ask", json={"question": "What should I prioritize?"}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == MOCK_ANSWER
    assert len(data["updated_history"]) == 2


@pytest.mark.asyncio
async def test_ask_with_conversation_history():
    prior_history = [
        {"role": "user", "content": "What is ARR?"},
        {"role": "assistant", "content": "ARR stands for Annual Recurring Revenue..."},
    ]
    with patch(
        "app.services.claude_client.chat",
        new=AsyncMock(return_value=(MOCK_ANSWER, MOCK_HISTORY)),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/ask",
                json={
                    "question": "How does that affect our valuation?",
                    "conversation_history": prior_history,
                },
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_ask_with_context():
    with patch(
        "app.services.claude_client.chat",
        new=AsyncMock(return_value=(MOCK_ANSWER, MOCK_HISTORY)),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/ask",
                json={
                    "question": "Should we raise now or wait?",
                    "context": {"revenue": "$5M ARR", "runway": "18 months"},
                },
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_ask_empty_question():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/ask", json={"question": ""})

    assert response.status_code == 422
