from datetime import datetime, timezone
from app.models import CompanyData, SalesAnalysis

def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)

def generate_report(company: CompanyData, analysis: SalesAnalysis) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Company Research Report: {company.company_name}

Generated: {generated_at}
Website: {company.website_url}

## Company Summary

{analysis.company_summary}

## Industry

{analysis.industry}

## Products / Services

{bullet_list(analysis.products_services)}

## Likely Pain Points

{bullet_list(analysis.likely_pain_points)}

## AI Automation Opportunities

{bullet_list(analysis.ai_opportunities)}

## Revenue Opportunities

{bullet_list(analysis.revenue_opportunities)}

## Suggested Sales Angle

{analysis.sales_angle}

## Meeting Talking Points

{bullet_list(analysis.meeting_talking_points)}

## Website Evidence

Pages reviewed:
{bullet_list(company.discovered_pages)}

Social links:
{bullet_list(company.social_links) if company.social_links else "- None found"}

Contact links:
{bullet_list(company.contact_links) if company.contact_links else "- None found"}

## Suggested Outreach Email Pitch

**Subject**: {analysis.prospect_email_subject}

{analysis.prospect_email_body}

## Confidence

{analysis.confidence}
"""
