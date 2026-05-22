# fund-lens

AI Financial Analyst API for PE-backed businesses and CFO teams, powered by Claude (Anthropic).

## Setup

### 1. Clone and install dependencies

```bash
cd fund-lens
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Endpoints

### `GET /health`

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok", "model": "claude-sonnet-4-6"}
```

---

### `POST /analyze`

Accepts structured financial metrics and returns an AI-generated narrative analysis.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {
      "company_name": "Acme SaaS",
      "revenue": 5000000,
      "burn_rate": 250000,
      "runway_months": 18,
      "ebitda_margin": -8.0,
      "gross_margin": 72.0,
      "revenue_growth_yoy": 95.0,
      "headcount": 38,
      "industry": "SaaS",
      "stage": "Series B"
    },
    "focus_areas": ["liquidity", "growth efficiency"]
  }'
```

**Response:**
```json
{
  "company_name": "Acme SaaS",
  "analysis": "Acme SaaS demonstrates strong growth momentum...",
  "key_insights": ["95% YoY growth is above SaaS benchmark of 60%", "..."],
  "risk_flags": ["18-month runway requires fundraise within 9-12 months"],
  "recommendations": ["Prioritize Rule of 40 improvement", "..."]
}
```

---

### `POST /ask`

Freeform CFO question with multi-turn conversation history.

**First turn:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "We have $4.5M ARR growing 90% YoY with 18 months of runway. Should we raise now or wait?",
    "context": {
      "company": "Acme SaaS",
      "stage": "Series B",
      "industry": "SaaS"
    }
  }'
```

**Follow-up turn (pass back updated_history):**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What multiple should we target?",
    "conversation_history": [
      {"role": "user", "content": "We have $4.5M ARR growing 90% YoY with 18 months of runway. Should we raise now or wait?"},
      {"role": "assistant", "content": "Given your metrics, raising now makes sense because..."}
    ]
  }'
```

**Response:**
```json
{
  "answer": "At 90% growth, you should target 12-15x ARR...",
  "updated_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "What multiple should we target?"},
    {"role": "assistant", "content": "At 90% growth, you should target 12-15x ARR..."}
  ]
}
```

---

### `POST /portfolio/compare`

Compare two companies side-by-side.

```bash
curl -X POST http://localhost:8000/portfolio/compare \
  -H "Content-Type: application/json" \
  -d '{
    "company_a": {
      "company_name": "GrowthCo",
      "revenue": 8000000,
      "ebitda_margin": 5.0,
      "gross_margin": 75.0,
      "revenue_growth_yoy": 110.0,
      "runway_months": 20,
      "industry": "SaaS",
      "stage": "Series B"
    },
    "company_b": {
      "company_name": "ProfitCo",
      "revenue": 14000000,
      "ebitda_margin": 18.0,
      "gross_margin": 68.0,
      "revenue_growth_yoy": 35.0,
      "runway_months": null,
      "industry": "SaaS",
      "stage": "Series C"
    },
    "comparison_criteria": ["growth", "profitability", "efficiency"]
  }'
```

**Response:**
```json
{
  "company_a_name": "GrowthCo",
  "company_b_name": "ProfitCo",
  "comparison": "GrowthCo is outpacing ProfitCo on growth at 110% vs 35% YoY...",
  "winner_by_category": {
    "growth": "GrowthCo",
    "profitability": "ProfitCo",
    "efficiency": "ProfitCo",
    "financial_health": "ProfitCo"
  },
  "summary": "ProfitCo is better positioned overall given its scale and profitability, though GrowthCo merits attention for its hypergrowth trajectory."
}
```

---

## Project Structure

```
fund-lens/
├── app/
│   ├── main.py                  # FastAPI app and router registration
│   ├── routers/
│   │   ├── analyze.py           # POST /analyze
│   │   ├── ask.py               # POST /ask
│   │   └── portfolio.py         # POST /portfolio/compare
│   ├── models/
│   │   ├── financial.py         # Pydantic models for metrics, analyze, compare
│   │   └── conversation.py      # Pydantic models for chat/ask
│   ├── services/
│   │   ├── claude_client.py     # All Anthropic API calls
│   │   └── prompt_builder.py    # Prompt construction logic
│   └── core/
│       └── config.py            # Settings via pydantic-settings
├── tests/
│   ├── test_analyze.py
│   ├── test_ask.py
│   └── test_portfolio.py
├── .env.example
├── README.md
└── requirements.txt
```
