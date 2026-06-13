import { useState } from "react";
import { ClipboardList, ExternalLink, Loader2, Mail, Search, Sparkles } from "lucide-react";
import { runResearch, sendOutreachEmail } from "./api";

function ListBlock({ title, items }) {
  return (
    <section className="panel-section">
      <h3>{title}</h3>
      <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
    </section>
  );
}

export default function App() {
  const [websiteUrl, setWebsiteUrl] = useState("https://nike.com");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Direct Client Outreach States
  const [prospectEmail, setProspectEmail] = useState("");
  const [outreachSubject, setOutreachSubject] = useState("");
  const [outreachBody, setOutreachBody] = useState("");
  const [outreachSending, setOutreachSending] = useState(false);
  const [outreachSuccess, setOutreachSuccess] = useState("");
  const [outreachError, setOutreachError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setProspectEmail("");
    setOutreachSubject("");
    setOutreachBody("");
    setOutreachSuccess("");
    setOutreachError("");
    try {
      const data = await runResearch({ website_url: websiteUrl, recipient_email: recipientEmail || null });
      setResult(data);
      if (data.company.discovered_emails && data.company.discovered_emails.length > 0) {
        setProspectEmail(data.company.discovered_emails[0]);
      }
      setOutreachSubject(data.analysis.prospect_email_subject || "");
      setOutreachBody(data.analysis.prospect_email_body || "");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSendOutreach(event) {
    event.preventDefault();
    setOutreachSending(true);
    setOutreachSuccess("");
    setOutreachError("");
    try {
      const response = await sendOutreachEmail({
        recipient_email: prospectEmail,
        subject: outreachSubject,
        body: outreachBody,
      });
      setOutreachSuccess(response.message || "Outreach email sent successfully!");
    } catch (err) {
      setOutreachError(err.message);
    } finally {
      setOutreachSending(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-row"><Sparkles size={24} /><span>Sales Co-Pilot</span></div>
        <form onSubmit={handleSubmit} className="research-form">
          <label htmlFor="website">Company website</label>
          <input id="website" value={websiteUrl} onChange={(event) => setWebsiteUrl(event.target.value)} placeholder="https://example.com" type="url" required />
          <label htmlFor="email">Email report</label>
          <input id="email" value={recipientEmail} onChange={(event) => setRecipientEmail(event.target.value)} placeholder="salesperson@company.com" type="email" />
          <button type="submit" disabled={loading}>{loading ? <Loader2 className="spin" size={18} /> : <Search size={18} />}{loading ? "Researching" : "Run Research"}</button>
        </form>
        <div className="workflow-list"><span>URL</span><span>Scrape</span><span>Clean</span><span>Analyze</span><span>Report</span></div>
      </aside>
      <section className="workspace">
        {!result && !error && (
          <div className="empty-state">
            <ClipboardList size={42} />
            <h1>Company intelligence, ready for the next sales conversation.</h1>
            <p>Enter a website and the agent will build a research brief with pain points, AI opportunities, and a sales angle.</p>
          </div>
        )}
        {error && <div className="error-box">{error}</div>}
        {result && (
          <article className="report-panel">
            <header className="report-header">
              <div>
                <p className="eyebrow">Research Report</p>
                <h1>{result.company.company_name}</h1>
                <a href={result.company.website_url} target="_blank" rel="noreferrer"><ExternalLink size={16} />{result.company.website_url}</a>
              </div>
              <div className="status-pill">{result.analysis.confidence}</div>
            </header>
            <section className="summary-band"><h2>{result.analysis.industry}</h2><p>{result.analysis.company_summary}</p></section>
            <ListBlock title="Products / Services" items={result.analysis.products_services} />
            <ListBlock title="Pain Points" items={result.analysis.likely_pain_points} />
            <ListBlock title="AI Opportunities" items={result.analysis.ai_opportunities} />
            <ListBlock title="Revenue Opportunities" items={result.analysis.revenue_opportunities} />
            <ListBlock title="Meeting Talking Points" items={result.analysis.meeting_talking_points} />
            <section className="panel-section sales-angle"><h3>Sales Angle</h3><p>{result.analysis.sales_angle}</p></section>
            
            {/* Direct Client Outreach Form */}
            <section className="outreach-box">
              <h3><Mail size={20} /> Direct Client Outreach</h3>
              <p style={{ fontSize: "0.9rem", color: "#536267", marginTop: 0, marginBottom: "16px" }}>
                Send a personalized sales pitch directly to the prospect. Select a discovered email address or enter one manually, and edit the pitch draft before sending.
              </p>
              
              {result.company.discovered_emails && result.company.discovered_emails.length > 0 && (
                <div className="email-badges-container">
                  <span className="email-badges-label">Discovered Emails (click to select):</span>
                  <div className="email-badges">
                    {result.company.discovered_emails.map((email) => (
                      <button 
                        key={email} 
                        type="button" 
                        className="email-badge" 
                        onClick={() => setProspectEmail(email)}
                      >
                        {email}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              <form onSubmit={handleSendOutreach} className="outreach-form-fields">
                <div className="outreach-form-group">
                  <label htmlFor="prospect-email">Recipient Email Address</label>
                  <input 
                    id="prospect-email" 
                    value={prospectEmail} 
                    onChange={(e) => setProspectEmail(e.target.value)} 
                    placeholder="prospect@company.com" 
                    type="email" 
                    required 
                  />
                </div>
                
                <div className="outreach-form-group">
                  <label htmlFor="outreach-subject">Email Subject</label>
                  <input 
                    id="outreach-subject" 
                    value={outreachSubject} 
                    onChange={(e) => setOutreachSubject(e.target.value)} 
                    placeholder="Email Subject" 
                    type="text" 
                    required 
                  />
                </div>
                
                <div className="outreach-form-group">
                  <label htmlFor="outreach-body">Email Pitch Body</label>
                  <textarea 
                    id="outreach-body" 
                    value={outreachBody} 
                    onChange={(e) => setOutreachBody(e.target.value)} 
                    placeholder="Write your email pitch here..." 
                    required 
                  />
                </div>
                
                <button 
                  type="submit" 
                  className="btn-send-outreach" 
                  disabled={outreachSending}
                >
                  {outreachSending ? <Loader2 className="spin" size={18} /> : <Mail size={18} />}
                  {outreachSending ? "Sending Outreach..." : "Send Pitch Email"}
                </button>
              </form>
              
              {outreachSuccess && <div className="outreach-alert-success">{outreachSuccess}</div>}
              {outreachError && <div className="outreach-alert-error">{outreachError}</div>}
            </section>

            <footer className="report-footer"><span>Saved record: {result.stored_record_id}</span><span>{result.email_sent ? <Mail size={16} /> : null}{result.email_sent ? "Email sent" : "Email not sent"}</span></footer>
          </article>
        )}
      </section>
    </main>
  );
}
