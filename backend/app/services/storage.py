from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from app.models import CompanyData, SalesAnalysis

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "company"

def save_research(reports_dir: Path, company: CompanyData, analysis: SalesAnalysis, report_markdown: str) -> tuple[str, str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    record_id = f"{slugify(company.company_name)}-{uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    markdown_path = reports_dir / f"{record_id}.md"
    json_path = reports_dir / f"{record_id}.json"
    index_path = reports_dir / "index.json"
    markdown_path.write_text(report_markdown, encoding="utf-8")
    json_path.write_text(json.dumps({"id": record_id, "created_at": created_at, "company": company.model_dump(), "analysis": analysis.model_dump(), "report_file": str(markdown_path)}, indent=2), encoding="utf-8")
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    index.append({"id": record_id, "company": company.company_name, "website_url": company.website_url, "created_at": created_at})
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return record_id, str(markdown_path)
