// Komunikacija sa FastAPI serverom (app.py). Sve adrese pocinju sa /api.
// U razvoju ih Vite prosledjuje na :8000 (vite.config.js), u produkciji ih sluzi isti server.

async function getJson(url, options) {
  const res = await fetch(url, options)
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.detail || `HTTP ${res.status}`)
  return body
}

export const api = {
  system: () => getJson('/api/system'),
  start: (topic) =>
    getJson('/api/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic }),
    }),
  events: (since) => getJson(`/api/events?since=${since}`),
  runs: () => getJson('/api/runs'),
  replay: (name) => getJson(`/api/replay?name=${encodeURIComponent(name)}`),
}
