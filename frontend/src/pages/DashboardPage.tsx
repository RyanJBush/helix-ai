import { useMemo } from 'react';

import { MOCK_AGGREGATES, MOCK_SENTIMENT_SERIES, MOCK_SIGNALS, WATCHLIST } from '../data/mockMarket';
import { useMarketStream } from '../hooks/useMarketStream';
import PageHeader from '../components/PageHeader';
import KpiCard from '../components/dashboard/KpiCard';
import SentimentChart from '../components/dashboard/SentimentChart';

function DashboardPage() {
  const { events, isLive } = useMarketStream(12);

  const kpis = useMemo(() => {
    const averageSentiment = (
      Object.values(MOCK_AGGREGATES).reduce((sum, item) => sum + item.avg_score, 0) / WATCHLIST.length
    ).toFixed(2);

    return [
      { label: 'Market Sentiment', value: averageSentiment, delta: '+0.03 today', tone: 'positive' as const },
      { label: 'Live Signals', value: String(MOCK_SIGNALS.length), delta: '2 BUY / 1 HOLD', tone: 'neutral' as const },
      { label: 'Stream Health', value: isLive ? 'Live' : 'Offline', delta: `${events.length} recent events`, tone: isLive ? 'positive' as const : 'negative' as const },
      { label: 'Tracked Tickers', value: String(WATCHLIST.length), delta: 'Large-cap focus', tone: 'neutral' as const },
    ];
  }, [events.length, isLive]);

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
    </section>
  );
}

export default DashboardPage;
