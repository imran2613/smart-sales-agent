from __future__ import annotations
import json
import re
from typing import Any
from openai import OpenAI
from app.config import Settings
from app.models import SalesAnalysis

SYSTEM_PROMPT = """You are a senior B2B sales research analyst. Return concise sales intelligence as valid JSON matching the requested schema."""

def infer_industry(text: str) -> str:
    lowered = text.lower()
    industry_keywords = {
        "E-commerce / Retail": ["shop", "cart", "shipping", "returns", "store", "apparel", "product"],
        "SaaS / Technology": ["software", "platform", "api", "cloud", "workflow", "automation", "dashboard"],
        "Healthcare": ["patient", "clinic", "health", "medical", "care", "hospital"],
        "Financial Services": ["bank", "loan", "payment", "insurance", "wealth", "credit"],
        "Education": ["student", "course", "learning", "school", "university", "training"],
        "Manufacturing": ["manufacturing", "factory", "supply chain", "equipment", "industrial"],
    }
    scores = {industry: sum(lowered.count(word) for word in words) for industry, words in industry_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General Business"

def extract_products_services(text: str) -> list[str]:
    candidates = []
    patterns = [r"we offer ([^.]+)", r"our products include ([^.]+)", r"solutions for ([^.]+)"]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            candidates.extend(re.split(r",| and |\|", match))
    cleaned = [item.strip().title() for item in candidates if 3 < len(item.strip()) < 60]
    return list(dict.fromkeys(cleaned))[:6] or ["Core products/services shown on website", "Customer experience", "Online sales or lead generation"]

def local_analysis(company_name: str, clean_text: str) -> SalesAnalysis:
    industry = infer_industry(clean_text)
    return SalesAnalysis(
        company_summary=f"{company_name} appears to operate in {industry.lower()} with a public website focused on products, services, brand credibility, and customer acquisition.",
        industry=industry,
        products_services=extract_products_services(clean_text),
        likely_pain_points=[
            "Converting anonymous website visitors into qualified sales conversations",
            "Handling repetitive customer questions across web and email channels",
            "Keeping product, service, and support information consistent across touchpoints",
            "Prioritizing high-intent accounts for sales follow-up",
        ],
        ai_opportunities=[
            "AI website concierge for product discovery and lead qualification",
            "Automated research briefs before sales calls",
            "AI support assistant trained on website and help content",
            "Personalized outreach generation by account segment",
        ],
        revenue_opportunities=[
            "Increase conversion from website traffic to booked meetings",
            "Shorten sales research time for account executives",
            "Improve upsell and cross-sell discovery using recommendation workflows",
        ],
        sales_angle="Lead with a practical AI assistant that answers buyer questions, qualifies intent, and routes sales-ready leads to the team.",
        meeting_talking_points=[
            "Ask which website questions currently create the most manual work",
            "Discuss where leads drop off before speaking with sales",
            "Explore whether support or sales teams repeat the same research tasks",
            "Offer a pilot around one high-value page or product category",
        ],
        confidence="Medium - based on public website text and heuristic analysis",
        prospect_email_subject=f"AI Automation and Revenue Opportunities for {company_name}",
        prospect_email_body=(
            f"Hi Team,\n\n"
            f"I recently analyzed the website for {company_name} and wanted to reach out regarding a few potential areas where "
            f"you might be able to leverage AI to drive more revenue and streamline operations.\n\n"
            f"Based on your offerings, I noticed that you could potentially increase website conversion rates by implementing "
            f"an AI website concierge to qualify customer intent, or optimize your support workflow using a custom AI assistant "
            f"trained on your product documentation.\n\n"
            f"I would love to set up a short 10-minute introduction call to discuss if any of these solutions align with your "
            f"current key priorities for this quarter.\n\n"
            f"Best regards,\n[Your Name]"
        ),
    )

def build_llm_prompt(company_name: str, clean_text: str) -> str:
    schema = SalesAnalysis.model_json_schema()
    return f"""Analyze this company for a B2B salesperson.
Company: {company_name}
Return JSON only using this schema:
{json.dumps(schema)}
Company website data:
{clean_text[:16000]}
"""

def parse_analysis(payload: str) -> SalesAnalysis:
    data: Any = json.loads(payload)
    return SalesAnalysis.model_validate(data)

def analyze_company(company_name: str, clean_text: str, settings: Settings) -> SalesAnalysis:
    if not settings.openai_api_key:
        return local_analysis(company_name, clean_text)
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_llm_prompt(company_name, clean_text)}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return parse_analysis(response.choices[0].message.content or "{}")
