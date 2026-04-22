import { useEffect, useMemo, useState } from 'react';

import PageHeader from '../components/PageHeader';
import { MOCK_SIGNALS, WATCHLIST } from '../data/mockMarket';
import { useMarketStream } from '../hooks/useMarketStream';
import { getWatchlistAlerts } from '../services/api';
import type { WatchlistAlert } from '../types/market';

function SignalsPage() {
  const { events } = useMarketStream(25);
  const [alerts, setAlerts] = useState<WatchlistAlert[]>([]);

  useEffect(() => {
    void (async () => {
      const data = await getWatchlistAlerts(WATCHLIST);
      setAlerts(data);
    })();
  }, []);

  const latestStreamScores = useMemo(() => {
    return events
      .filter((item) => item.event === 'sentiment_update' && item.ticker && item.score !== undefined)
      .slice(0, 5)
      .map((item) => `${item.ticker}: ${item.score}`);
  }, [events]);

  return (
    <section>
      <PageHeader title="Signals" subtitle="Model-derived buy/sell/hold opportunities" />

      <article className="panel">
        <table className="signals-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Signal</th>
              <th>Confidence</th>
              <th>Rationale</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_SIGNALS.map((signal) => (
              <tr key={signal.ticker}>
                <td>{signal.ticker}</td>
                <td>
                  <span className={`badge ${signal.signal === 'BUY' ? 'positive' : signal.signal === 'SELL' ? 'negative' : 'neutral'}`}>
                    {signal.signal}
                  </span>
                </td>
                <td>{(signal.confidence * 100).toFixed(1)}%</td>
                <td>{signal.rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      <article className="panel">
        <h3>Recent Stream Scores</h3>
        <p className="muted">{latestStreamScores.join(' | ') || 'Awaiting stream updates...'}</p>
      </article>

      <article className="panel">
        <h3>Active Alerts</h3>
        <ul className="event-list">
          {alerts.length ? (
            alerts.map((alert) => (
              <li key={`${alert.ticker}-${alert.alert_type}`}>
                <strong>{alert.ticker}</strong> {alert.alert_type} • {(alert.confidence * 100).toFixed(0)}%
              </li>
            ))
          ) : (
            <li>No active alerts.</li>
          )}
        </ul>
      </article>
    </section>
  );
}

export default SignalsPage;
