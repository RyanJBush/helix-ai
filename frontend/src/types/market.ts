export interface TickerAggregation {
  ticker: string;
  article_count: number;
  avg_score: number;
  positive_ratio: number;
  neutral_ratio: number;
  negative_ratio: number;
  window_start: string;
  window_end: string;
}

export interface Signal {
  ticker: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  rationale: string;
  generated_at: string;
}

export interface NewsItem {
  ticker: string;
  source: string;
  headline: string;
  content: string;
  published_at: string;
}

export interface StreamEvent {
  event: string;
  ticker?: string;
  score?: number;
  label?: string;
  timestamp?: string;
  payload?: string;
}
