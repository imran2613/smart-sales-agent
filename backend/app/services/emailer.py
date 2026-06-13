from __future__ import annotations
import smtplib
import logging
from email.message import EmailMessage
from app.config import Settings
from app.models import CompanyData, SalesAnalysis

logger = logging.getLogger("app.emailer")

def can_send_email(settings: Settings) -> bool:
    return all([settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.email_from])

def send_report_email(recipient: str, company: CompanyData, analysis: SalesAnalysis, report_markdown: str, settings: Settings) -> bool:
    if not recipient or not can_send_email(settings):
        return False
    try:
        message = EmailMessage()
        message["Subject"] = f"{company.company_name} Research Complete"
        message["From"] = settings.email_from
        message["To"] = recipient
        message.set_content(f"Company research is complete.\n\nKey opportunity:\n{analysis.sales_angle}\n")
        message.add_attachment(report_markdown, subtype="markdown", filename=f"{company.company_name}-research.md")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
    except Exception as e:
        logger.error(f"Failed to send report email: {e}", exc_info=True)
        return False

def send_custom_email(recipient: str, subject: str, body: str, settings: Settings) -> bool:
    if not recipient or not can_send_email(settings):
        return False
    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.email_from
        message["To"] = recipient
        message.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
    except Exception as e:
        logger.error(f"Failed to send custom email: {e}", exc_info=True)
        return False

