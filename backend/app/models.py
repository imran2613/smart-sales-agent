from pydantic import BaseModel, Field, HttpUrl

class ResearchRequest(BaseModel):
    website_url: HttpUrl
    recipient_email: str | None = Field(default=None)

class CompanyData(BaseModel):
    company_name: str
    website_url: str
    discovered_pages: list[str]
    social_links: list[str]
    contact_links: list[str]
    raw_text: str
    clean_text: str
    discovered_emails: list[str] = Field(default_factory=list)

class SalesAnalysis(BaseModel):
    company_summary: str
    industry: str
    products_services: list[str]
    likely_pain_points: list[str]
    ai_opportunities: list[str]
    revenue_opportunities: list[str]
    sales_angle: str
    meeting_talking_points: list[str]
    confidence: str
    prospect_email_subject: str = Field(default="", description="A personalized and compelling subject line for a cold outreach email to the company owner.")
    prospect_email_body: str = Field(default="", description="A personalized and compelling cold outreach email body pitching the sales angle and AI opportunities. Keep it concise, professional, and friendly.")

class OutreachEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    body: str

class ResearchResponse(BaseModel):
    company: CompanyData
    analysis: SalesAnalysis
    report_markdown: str
    report_file: str
    stored_record_id: str
    email_sent: bool = False
