from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
import requests
from bs4 import BeautifulSoup
from app.config import Settings
from app.services.cleaner import clean_website_text

IMPORTANT_PATH_HINTS = ("about", "product", "service", "solution", "contact", "blog", "news", "pricing")
SOCIAL_HOSTS = ("linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "youtube.com", "tiktok.com")
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

@dataclass
class ScrapedWebsite:
    company_name: str
    website_url: str
    discovered_pages: list[str]
    social_links: list[str]
    contact_links: list[str]
    raw_text: str
    clean_text: str
    discovered_emails: list[str]

def same_domain(url: str, base_netloc: str) -> bool:
    host = urlparse(url).netloc.replace("www.", "")
    return host == base_netloc.replace("www.", "")

def absolute_url(href: str, base_url: str) -> str | None:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    parsed = urlparse(urljoin(base_url, href))
    if parsed.scheme not in {"http", "https"}:
        return None
    return parsed._replace(fragment="").geturl()

def extract_visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg", "form", "nav", "footer"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)

def score_link(url: str) -> int:
    path = urlparse(url).path.lower()
    return sum(5 for hint in IMPORTANT_PATH_HINTS if hint in path) - path.count("/")

def fetch_page(url: str, settings: Settings) -> tuple[BeautifulSoup, str]:
    response = requests.get(url, headers={"User-Agent": settings.user_agent}, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup, extract_visible_text(soup)

def scrape_website(url: str, settings: Settings) -> ScrapedWebsite:
    start_url = str(url)
    parsed_start = urlparse(start_url)
    base_netloc = parsed_start.netloc
    pages_to_visit = [start_url]
    visited, raw_chunks = [], []
    social_links, contact_links, discovered_emails = set(), set(), set()
    company_name = parsed_start.netloc.replace("www.", "").split(".")[0].title()

    while pages_to_visit and len(visited) < settings.max_pages:
        current = pages_to_visit.pop(0)
        if current in visited:
            continue
        try:
            soup, text = fetch_page(current, settings)
        except requests.RequestException:
            continue
        visited.append(current)
        raw_chunks.append(text)
        
        # Extract emails from the page
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href.startswith("mailto:"):
                email = href[7:].split("?")[0].strip().lower()
                if EMAIL_REGEX.match(email):
                    discovered_emails.add(email)
        
        for email in EMAIL_REGEX.findall(text):
            cleaned = email.strip().lower()
            if not cleaned.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js')):
                discovered_emails.add(cleaned)

        if soup.title and soup.title.string and len(visited) == 1:
            company_name = soup.title.string.split("|")[0].split("-")[0].strip()[:80] or company_name
        for link in soup.find_all("a", href=True):
            target = absolute_url(link.get("href", ""), current)
            if not target:
                continue
            lowered = target.lower()
            if any(host in lowered for host in SOCIAL_HOSTS):
                social_links.add(target)
                continue
            if "contact" in lowered:
                contact_links.add(target)
            if same_domain(target, base_netloc) and target not in visited and target not in pages_to_visit:
                pages_to_visit.append(target)
        pages_to_visit = sorted(pages_to_visit, key=score_link, reverse=True)

    raw_text = "\n".join(raw_chunks)
    return ScrapedWebsite(
        company_name, 
        start_url, 
        visited, 
        sorted(social_links), 
        sorted(contact_links), 
        raw_text, 
        clean_website_text(raw_text),
        sorted(discovered_emails)
    )
