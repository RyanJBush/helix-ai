const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://127.0.0.1:8000/ws/stream'

const fallback = {
  summary: {
    total_articles: 0,
    analyzed_articles: 0,
    tracked_tickers: 0,
    bullish_tickers: 0,
    bearish_tickers: 0,
  },
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`)
  }
  return response.json()
}

export async function ingestSimulatedNews(simulateCount = 5) {
  try {
    return await request('/api/data/ingest', {
      method: 'POST',
      body: JSON.stringify({ simulate_count: simulateCount, articles: [] }),
    })
  } catch {
    return { ingested: 0, items: [] }
  }
}

export async function runSentimentAnalysis() {
  try {
    return await request('/api/sentiment/analyze', {
      method: 'POST',
      body: JSON.stringify({}),
    })
  } catch {
    return { analyzed: 0, items: [] }
  }
}

export async function fetchSummary() {
  try {
    return await request('/api/dashboard/summary')
  } catch {
    return fallback.summary
  }
}

export async function fetchNews(ticker = '') {
  const query = ticker ? `?ticker=${encodeURIComponent(ticker)}` : ''
  try {
    const payload = await request(`/api/data/news${query}`)
    return payload.items ?? []
  } catch {
    return []
  }
}

export async function fetchTickerSentiment(ticker) {
  if (!ticker) {
    return null
  }

  try {
    return await request(`/api/sentiment/${ticker}`)
  } catch {
    return null
  }
}

export async function fetchTickerSignal(ticker) {
  if (!ticker) {
    return null
  }

  try {
    return await request(`/api/signals/${ticker}`)
  } catch {
    return null
  }
}

export function connectStream(onMessage) {
  const ws = new WebSocket(WS_URL)
  ws.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data))
    } catch {
      // ignore invalid stream payloads
    }
  }
  return ws
}
