import type { NewsItem, Signal, TickerAggregation } from '../types/market';

export const WATCHLIST = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN'];

export const MOCK_AGGREGATES: Record<string, TickerAggregation> = {
  AAPL: {
    ticker: 'AAPL',
    article_count: 23,
    avg_score: 0.78,
    positive_ratio: 0.69,
    neutral_ratio: 0.22,
    negative_ratio: 0.09,
    window_start: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    window_end: new Date().toISOString(),
  },
  MSFT: {
    ticker: 'MSFT',
    article_count: 17,
    avg_score: 0.67,
    positive_ratio: 0.54,
    neutral_ratio: 0.31,
    negative_ratio: 0.15,
    window_start: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    window_end: new Date().toISOString(),
  },
  TSLA: {
    ticker: 'TSLA',
    article_count: 28,
    avg_score: 0.43,
    positive_ratio: 0.18,
    neutral_ratio: 0.34,
    negative_ratio: 0.48,
    window_start: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    window_end: new Date().toISOString(),
  },
  NVDA: {
    ticker: 'NVDA',
    article_count: 21,
    avg_score: 0.81,
    positive_ratio: 0.74,
    neutral_ratio: 0.18,
    negative_ratio: 0.08,
    window_start: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    window_end: new Date().toISOString(),
  },
  AMZN: {
    ticker: 'AMZN',
    article_count: 16,
    avg_score: 0.61,
    positive_ratio: 0.49,
    neutral_ratio: 0.29,
    negative_ratio: 0.22,
    window_start: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    window_end: new Date().toISOString(),
  },
};

export const MOCK_SIGNALS: Signal[] = [
  { ticker: 'NVDA', signal: 'BUY', confidence: 0.74, rationale: 'AI demand remains durable', generated_at: new Date().toISOString() },
  { ticker: 'AAPL', signal: 'BUY', confidence: 0.69, rationale: 'Services momentum offsets hardware risk', generated_at: new Date().toISOString() },
  { ticker: 'AMZN', signal: 'HOLD', confidence: 0.49, rationale: 'Mixed sentiment breadth', generated_at: new Date().toISOString() },
  { ticker: 'TSLA', signal: 'SELL', confidence: 0.48, rationale: 'Persistent pricing pressure concerns', generated_at: new Date().toISOString() },
];

export const MOCK_NEWS: NewsItem[] = [
  { ticker: 'NVDA', source: 'mock-wire', headline: 'NVIDIA suppliers report improving lead times', content: 'Supply chain execution improves for AI accelerators.', published_at: new Date().toISOString() },
  { ticker: 'AAPL', source: 'mock-wire', headline: 'Apple expands buyback authorization', content: 'Capital return remains a tailwind for investor confidence.', published_at: new Date().toISOString() },
  { ticker: 'TSLA', source: 'mock-wire', headline: 'Tesla updates pricing strategy in Europe', content: 'Investors weigh demand elasticity versus margin pressure.', published_at: new Date().toISOString() },
  { ticker: 'MSFT', source: 'mock-wire', headline: 'Microsoft signs major cloud AI deal', content: 'Enterprise AI workloads continue scaling.', published_at: new Date().toISOString() },
];

export const MOCK_SENTIMENT_SERIES = [0.58, 0.61, 0.63, 0.62, 0.67, 0.7, 0.66, 0.72, 0.78, 0.74, 0.79, 0.82];
