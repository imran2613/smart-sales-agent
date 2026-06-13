# Sales Research Co-Pilot Agent

Full-stack MVP agent that accepts a company website URL, scrapes public pages, cleans the text, analyzes the business with an LLM or local fallback, generates a sales research report, stores it locally, and can optionally email the salesperson.

## Workflow

```text
User enters URL -> Scraper -> Cleaner -> LLM/local analyzer -> Report -> Storage -> Optional email
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
API: http://localhost:8000

## Optional LLM

Add to `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Without an API key, the app uses a local heuristic analyzer.

## Optional Email

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=you@example.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=you@example.com
```

## API Example

```bash
curl -X POST http://localhost:8000/api/research -H "Content-Type: application/json" -d "{\"website_url\":\"https://nike.com\"}"
```
