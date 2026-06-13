import argparse
from app.config import get_settings
from app.models import CompanyData
from app.services.analyzer import analyze_company
from app.services.report import generate_report
from app.services.scraper import scrape_website
from app.services.storage import save_research

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Sales Research Co-Pilot from the command line.")
    parser.add_argument("website_url")
    args = parser.parse_args()
    settings = get_settings()
    scraped = scrape_website(args.website_url, settings)
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
    report = generate_report(company, analysis)
    record_id, report_file = save_research(settings.reports_dir, company, analysis, report)
    print(f"Saved report {record_id}: {report_file}")
    print(report)

if __name__ == "__main__":
    main()
