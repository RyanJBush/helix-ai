import { MOCK_AGGREGATES, MOCK_NEWS, MOCK_SIGNALS } from '../data/mockMarket';
import type { NewsItem, Signal, TickerAggregation } from '../types/market';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function fetchJson<T>(url: string, init?: RequestInit, fallback?: T): Promise<T> {
  try {
    const response = await fetch(url, init);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    if (fallback !== undefined) {
      return fallback;
    }
    throw new Error('Failed to fetch API response');
  }
}

export async function getTickerAggregation(ticker: string): Promise<TickerAggregation> {
  return fetchJson(`${API_BASE}/analytics/ticker/${ticker}`, undefined, MOCK_AGGREGATES[ticker] ?? MOCK_AGGREGATES.AAPL);
}

export async function getTickerSignal(ticker: string): Promise<Signal> {
  return fetchJson(`${API_BASE}/signals/ticker/${ticker}`, undefined, MOCK_SIGNALS.find((item) => item.ticker === ticker) ?? MOCK_SIGNALS[0]);
}

export async function ingestNews(tickers: string[]): Promise<NewsItem[]> {
  return fetchJson(
    `${API_BASE}/news/ingest`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tickers, limit_per_ticker: 3 }),
    },
    MOCK_NEWS,
  );
}
