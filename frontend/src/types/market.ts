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
  alert?: string | null;
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

export interface DashboardOverview {
  lookback_hours: number;
  articles_processed: number;
  avg_sentiment_score: number;
  avg_confidence: number;
  watchlist_alerts: number;
  most_mentioned_tickers: string[];
}

export interface EventDistributionItem {
  event_type: string;
  count: number;
}

export interface TopicClusterSummary {
  topic: string;
  mentions: number;
  sample_tickers: string[];
}

export interface TickerArticleRow {
  sentiment_record_id: number;
  ticker: string;
  source: string;
  label: string;
  score: number;
  confidence: number;
  model_used: string;
  timestamp: string;
  text_preview: string;
}

export interface TickerArticleTable {
  ticker: string;
  lookback_hours: number;
  total: number;
  limit: number;
  offset: number;
  rows: TickerArticleRow[];
}

export interface WatchlistAlert {
  ticker: string;
  signal: string;
  alert_type: string;
  confidence: number;
  detail: string;
}
