import { MOCK_AGGREGATES, MOCK_NEWS, MOCK_SIGNALS } from '../data/mockMarket';
import type {
  DashboardOverview,
  EventDistributionItem,
  NewsItem,
  Signal,
  TickerAggregation,
  TickerArticleTable,
  TopicClusterSummary,
  WatchlistAlert,
} from '../types/market';

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

export async function getDashboardOverview(watchlist: string[]): Promise<DashboardOverview> {
  const query = new URLSearchParams();
  query.set('lookback_hours', '24');
  watchlist.forEach((ticker) => query.append('watchlist', ticker));

  const fallback: DashboardOverview = {
    lookback_hours: 24,
    articles_processed: 105,
    avg_sentiment_score: 0.64,
    avg_confidence: 0.62,
    watchlist_alerts: 2,
    most_mentioned_tickers: watchlist,
  };
  return fetchJson(`${API_BASE}/analytics/overview?${query.toString()}`, undefined, fallback);
}

export async function getEventDistribution(): Promise<EventDistributionItem[]> {
  return fetchJson(`${API_BASE}/analytics/events/distribution?lookback_hours=72`, undefined, [
    { event_type: 'earnings', count: 18 },
    { event_type: 'macro_news', count: 9 },
    { event_type: 'social_sentiment', count: 13 },
  ]);
}

export async function getTopicClusters(): Promise<TopicClusterSummary[]> {
  return fetchJson(`${API_BASE}/analytics/topics/clusters?lookback_hours=72`, undefined, [
    { topic: 'earnings', mentions: 22, sample_tickers: ['AAPL', 'NVDA'] },
    { topic: 'macro', mentions: 7, sample_tickers: ['TSLA', 'AMZN'] },
  ]);
}

export async function getTickerArticleTable(ticker: string): Promise<TickerArticleTable> {
  return fetchJson(`${API_BASE}/analytics/ticker/${ticker}/articles?lookback_hours=72&limit=10&offset=0`, undefined, {
    ticker,
    lookback_hours: 72,
    total: 2,
    limit: 10,
    offset: 0,
    rows: [
      {
        sentiment_record_id: 1,
        ticker,
        source: 'mock-wire',
        label: 'positive',
        score: 0.78,
        confidence: 0.66,
        model_used: 'finbert_fallback',
        timestamp: new Date().toISOString(),
        text_preview: `Sample sentiment text for ${ticker}`,
      },
    ],
  });
}

export async function getWatchlistAlerts(tickers: string[]): Promise<WatchlistAlert[]> {
  const query = new URLSearchParams();
  tickers.forEach((ticker) => query.append('tickers', ticker));
  query.set('lookback_hours', '72');

  const fallback: WatchlistAlert[] = [
    {
      ticker: 'TSLA',
      signal: 'HOLD',
      alert_type: 'low_confidence',
      confidence: 0.41,
      detail: 'Signal confidence below 0.50; monitoring only.',
    },
  ];
  const response = await fetchJson<{ generated_at: string; alerts: WatchlistAlert[] }>(
    `${API_BASE}/signals/watchlist/alerts?${query.toString()}`,
    undefined,
    { generated_at: new Date().toISOString(), alerts: fallback },
  );
  return response.alerts;
}
