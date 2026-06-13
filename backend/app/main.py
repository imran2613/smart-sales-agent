from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models import CompanyData, ResearchRequest, ResearchResponse, OutreachEmailRequest
from app.services.analyzer import analyze_company
from app.services.emailer import send_report_email, send_custom_email, can_send_email
from app.services.report import generate_report
from app.services.scraper import scrape_website
from app.services.storage import save_research

app = FastAPI(title="Sales Research Co-Pilot Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/research", response_model=ResearchResponse)
def research_company(payload: ResearchRequest) -> ResearchResponse:
    settings = get_settings()
    scraped = scrape_website(str(payload.website_url), settings)
    if not scraped.clean_text:
        raise HTTPException(status_code=422, detail="Could not extract useful text from this website.")
    company = CompanyData(
        company_name=scraped.company_name,
        website_url=scraped.website_url,
        discovered_pages=scraped.discovered_pages,
        social_links=scraped.social_links,
        contact_links=scraped.contact_links,
        raw_text=scraped.raw_text,
        clean_text=scraped.clean_text,
        discovered_emails=scraped.discovered_emails,
    )
    analysis = analyze_company(company.company_name, company.clean_text, settings)
    report_markdown = generate_report(company, analysis)
    record_id, report_file = save_research(settings.reports_dir, company, analysis, report_markdown)
    email_sent = False
    if payload.recipient_email:
        email_sent = send_report_email(payload.recipient_email, company, analysis, report_markdown, settings)
    return ResearchResponse(company=company, analysis=analysis, report_markdown=report_markdown, report_file=report_file, stored_record_id=record_id, email_sent=email_sent)

@app.post("/api/send-outreach")
def send_outreach(payload: OutreachEmailRequest) -> dict[str, str]:
    settings = get_settings()
    if not can_send_email(settings):
        raise HTTPException(
            status_code=400,
            detail="SMTP configuration is missing. Please configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and EMAIL_FROM in your backend .env file to enable sending email outreach directly."
        )
    success = send_custom_email(payload.recipient_email, payload.subject, payload.body, settings)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send outreach email. Please verify SMTP credentials and settings.")
    return {"status": "success", "message": "Outreach email sent successfully!"}
