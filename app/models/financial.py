from pydantic import BaseModel, Field
from typing import Optional


class FinancialMetrics(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    revenue: float = Field(..., gt=0, description="Annual revenue in USD")
    burn_rate: Optional[float] = Field(None, ge=0, description="Monthly cash burn in USD")
    runway_months: Optional[float] = Field(None, ge=0, description="Months of runway remaining")
    ebitda_margin: Optional[float] = Field(None, ge=-100, le=100, description="EBITDA margin as a percentage")
    gross_margin: Optional[float] = Field(None, ge=-100, le=100, description="Gross margin as a percentage")
    revenue_growth_yoy: Optional[float] = Field(None, description="Year-over-year revenue growth as a percentage")
    headcount: Optional[int] = Field(None, gt=0, description="Number of employees")
    industry: Optional[str] = Field(None, description="Industry vertical")
    stage: Optional[str] = Field(None, description="Company stage (e.g., Series A, Series B, Growth)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "Acme SaaS",
                "revenue": 5000000,
                "burn_rate": 250000,
                "runway_months": 18,
                "ebitda_margin": -8.0,
                "gross_margin": 72.0,
                "revenue_growth_yoy": 95.0,
                "headcount": 38,
                "industry": "SaaS",
                "stage": "Series B",
            }
        }
    }


class AnalyzeRequest(BaseModel):
    metrics: FinancialMetrics
    focus_areas: Optional[list[str]] = Field(
        None,
        description="Specific areas to focus on (e.g., ['liquidity', 'profitability', 'growth'])",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
                    "stage": "Series B",
                },
                "focus_areas": ["liquidity", "burn efficiency"],
            }
        }
    }


class AnalyzeResponse(BaseModel):
    company_name: str
    analysis: str
    key_insights: list[str]
    risk_flags: list[str]
    recommendations: list[str]


class CompareRequest(BaseModel):
    company_a: FinancialMetrics
    company_b: FinancialMetrics
    comparison_criteria: Optional[list[str]] = Field(
        None,
        description="Specific criteria to compare (e.g., ['efficiency', 'growth', 'profitability'])",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_a": {
                    "company_name": "GrowthCo",
                    "revenue": 8000000,
                    "ebitda_margin": 5.0,
                    "gross_margin": 75.0,
                    "revenue_growth_yoy": 110.0,
                    "runway_months": 20,
                    "industry": "SaaS",
                    "stage": "Series B",
                },
                "company_b": {
                    "company_name": "ProfitCo",
                    "revenue": 14000000,
                    "ebitda_margin": 18.0,
                    "gross_margin": 68.0,
                    "revenue_growth_yoy": 35.0,
                    "industry": "SaaS",
                    "stage": "Series C",
                },
                "comparison_criteria": ["growth", "profitability", "efficiency"],
            }
        }
    }


class CompareResponse(BaseModel):
    company_a_name: str
    company_b_name: str
    comparison: str
    winner_by_category: dict[str, str]
    summary: str
