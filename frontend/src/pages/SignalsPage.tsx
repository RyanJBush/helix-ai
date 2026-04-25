import { useEffect, useMemo, useState } from 'react';

import PageHeader from '../components/PageHeader';
import { WATCHLIST } from '../data/mockMarket';
import { useMarketStream } from '../hooks/useMarketStream';
import { getBacktestScenarios, getWatchlistAlerts, getWatchlistSignals } from '../services/api';
import type { ScenarioBacktestResponse, Signal, WatchlistAlert } from '../types/market';

function SignalsPage() {
  const { events } = useMarketStream(25);
  const [alerts, setAlerts] = useState<WatchlistAlert[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [scenarioReport, setScenarioReport] = useState<ScenarioBacktestResponse | null>(null);

  useEffect(() => {
    void (async () => {
      const [alertData, signalData] = await Promise.all([getWatchlistAlerts(WATCHLIST), getWatchlistSignals(WATCHLIST)]);
      setAlerts(alertData);
      setSignals(signalData);
      const scenarioData = await getBacktestScenarios(WATCHLIST[0]);
      setScenarioReport(scenarioData);
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
            {signals.map((signal) => (
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
                <strong>{alert.ticker}</strong> {alert.alert_type} • {alert.severity} • {(alert.confidence * 100).toFixed(0)}%
              </li>
            ))
          ) : (
            <li>No active alerts.</li>
          )}
        </ul>
      </article>

      <article className="panel">
        <h3>Backtest Scenario Leaderboard ({scenarioReport?.ticker ?? WATCHLIST[0]})</h3>
        <table className="signals-table">
          <thead>
            <tr>
              <th>Scenario</th>
              <th>Hit Rate</th>
              <th>Sharpe-like</th>
              <th>Proxy Return</th>
              <th>Relative Return</th>
            </tr>
          </thead>
          <tbody>
            {(scenarioReport?.scenarios ?? []).map((row) => (
              <tr key={row.scenario}>
                <td>{row.scenario}</td>
                <td>{(row.hit_rate * 100).toFixed(0)}%</td>
                <td>{row.sharpe_like_ratio.toFixed(2)}</td>
                <td>{(row.cumulative_proxy_return * 100).toFixed(1)}%</td>
                <td>{(row.cumulative_relative_return * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}

export default SignalsPage;
