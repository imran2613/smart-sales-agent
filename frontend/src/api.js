const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function runResearch(payload) {
  const response = await fetch(API_BASE_URL + "/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Research failed");
  }
  return response.json();
}

export async function sendOutreachEmail(payload) {
  const response = await fetch(API_BASE_URL + "/api/send-outreach", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to send outreach email");
  }
  return response.json();
}
