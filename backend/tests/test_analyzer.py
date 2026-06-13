from app.services.analyzer import local_analysis

def test_local_analysis_returns_sales_fields():
    result = local_analysis("Acme", "We offer cloud software, workflow automation, and dashboards for teams.")
    assert result.industry == "SaaS / Technology"
    assert result.ai_opportunities
    assert result.meeting_talking_points
