import { useEffect, useMemo, useState } from 'react';

import { MOCK_SENTIMENT_SERIES, WATCHLIST } from '../data/mockMarket';
import { useMarketStream } from '../hooks/useMarketStream';
import PageHeader from '../components/PageHeader';
import KpiCard from '../components/dashboard/KpiCard';
import SentimentChart from '../components/dashboard/SentimentChart';
import { getDashboardOverview, getEventDistribution, getTopicClusters, getWatchlistAlerts } from '../services/api';
import type { DashboardOverview, EventDistributionItem, TopicClusterSummary, WatchlistAlert } from '../types/market';

function DashboardPage() {
  const { events, isLive } = useMarketStream(12);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [eventDistribution, setEventDistribution] = useState<EventDistributionItem[]>([]);
  const [clusters, setClusters] = useState<TopicClusterSummary[]>([]);
  const [alerts, setAlerts] = useState<WatchlistAlert[]>([]);

  useEffect(() => {
    void (async () => {
      const [overviewData, distributionData, clusterData, alertData] = await Promise.all([
        getDashboardOverview(WATCHLIST),
        getEventDistribution(),
        getTopicClusters(),
        getWatchlistAlerts(WATCHLIST),
      ]);
      setOverview(overviewData);
      setEventDistribution(distributionData);
      setClusters(clusterData);
      setAlerts(alertData);
    })();
  }, []);

  const kpis = useMemo(() => {
    const averageSentiment = (overview?.avg_sentiment_score ?? 0).toFixed(2);
    const watchlistAlerts = overview?.watchlist_alerts ?? alerts.length;

    return [
      { label: 'Market Sentiment', value: averageSentiment, delta: '+0.03 today', tone: 'positive' as const },
      { label: 'Articles Processed', value: String(overview?.articles_processed ?? 0), delta: '24h coverage', tone: 'neutral' as const },
      { label: 'Watchlist Alerts', value: String(watchlistAlerts), delta: 'Sharp shift + low confidence', tone: watchlistAlerts > 0 ? 'negative' as const : 'positive' as const },
      { label: 'Stream Health', value: isLive ? 'Live' : 'Offline', delta: `${events.length} recent events`, tone: isLive ? 'positive' as const : 'negative' as const },
      { label: 'Top Mentioned', value: overview?.most_mentioned_tickers[0] ?? WATCHLIST[0], delta: 'Most covered ticker', tone: 'neutral' as const },
    ];
  }, [alerts.length, events.length, isLive, overview]);

  return (
    <section>
      <PageHeader title="Dashboard" subtitle="Real-time sentiment and trading pulse" />

      <div className="kpi-grid">
        {kpis.map((kpi) => (
          <KpiCard key={kpi.label} label={kpi.label} value={kpi.value} delta={kpi.delta} tone={kpi.tone} />
        ))}
      </div>

      <div className="panel-grid">
        <SentimentChart title="24h sentiment trend" values={MOCK_SENTIMENT_SERIES} />
        <article className="panel">
          <h3>Live Event Tape</h3>
          <ul className="event-list">
            {events.slice(0, 8).map((event, index) => (
              <li key={`${event.timestamp ?? index}-${index}`}>
                <strong>{event.ticker ?? 'MKT'}</strong> {event.event}
                {event.score ? ` • score ${event.score}` : ''}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <div className="panel-grid">
        <article className="panel">
          <h3>Event Distribution</h3>
          <ul className="event-list">
            {eventDistribution.slice(0, 5).map((item) => (
              <li key={item.event_type}>
                <strong>{item.event_type}</strong> • {item.count} mentions
              </li>
            ))}
          </ul>
        </article>
        <article className="panel">
          <h3>Recurring Topic Clusters</h3>
          <ul className="event-list">
            {clusters.slice(0, 5).map((item) => (
              <li key={item.topic}>
                <strong>{item.topic}</strong> • {item.mentions} mentions • {item.sample_tickers.join(', ')}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="panel">
        <h3>Alert Center</h3>
        <ul className="event-list">
          {alerts.length ? (
            alerts.map((alert) => (
              <li key={`${alert.ticker}-${alert.alert_type}`}>
                <strong>{alert.ticker}</strong> {alert.alert_type} • {(alert.confidence * 100).toFixed(0)}% • {alert.detail}
              </li>
            ))
          ) : (
            <li>No active watchlist alerts.</li>
          )}
        </ul>
      </article>
    </section>
  );
}

export default DashboardPage;
