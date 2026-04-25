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
  weighted_score?: number;
  signal_strength?: number;
  factors?: Record<string, number>;
  buy_threshold?: number;
  sell_threshold?: number;
  min_confidence?: number;
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

export interface TickerMetricSnapshot {
  timestamp: string;
  article_count: number;
  weighted_sentiment_score: number;
  weighted_confidence: number;
  positive_ratio: number;
  neutral_ratio: number;
  negative_ratio: number;
}

export interface TickerMetricsResponse {
  ticker: string;
  bucket_hours: number;
  lookback_hours: number;
  points: TickerMetricSnapshot[];
}

export interface IngestAndScoreSummary {
  run_id: number;
  tickers: string[];
  news_items_inserted: number;
  sentiments_created: number;
  signals_created: number;
}

export interface WatchlistAlert {
  ticker: string;
  signal: string;
  alert_type: string;
  severity: 'high' | 'medium' | 'low';
  confidence: number;
  detail: string;
}

export interface SentimentMetricPoint {
  timestamp: string;
  label: string;
  score: number;
  confidence: number;
  source: string;
  source_weight: number;
}

export interface SignalMetricPoint {
  timestamp: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  weighted_score: number;
  rationale: string;
}

export interface TickerDrilldownResponse {
  ticker: string;
  lookback_hours: number;
  aggregate: TickerAggregation;
  sentiment_history: SentimentMetricPoint[];
  signal_history: SignalMetricPoint[];
}

export interface SignalContributor {
  sentiment_record_id: number;
  source: string;
  label: string;
  score: number;
  confidence: number;
  contribution_weight: number;
}

export interface SourceContradiction {
  source: string;
  positive_count: number;
  negative_count: number;
}

export interface SignalExplanationResponse {
  ticker: string;
  lookback_hours: number;
  generated_signal: string;
  generated_confidence: number;
  confidence_disclaimer?: string | null;
  top_contributors: SignalContributor[];
  contradictions: SourceContradiction[];
  generated_at: string;
}
