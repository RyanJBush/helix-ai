import { useEffect, useMemo, useState } from 'react';

import PageHeader from '../components/PageHeader';
import TickerFilter from '../components/dashboard/TickerFilter';
import SentimentChart from '../components/dashboard/SentimentChart';
import { WATCHLIST } from '../data/mockMarket';
import { getTickerAggregation, getTickerArticleTable, getTickerSignal } from '../services/api';
import type { Signal, TickerAggregation, TickerArticleTable } from '../types/market';

function TickerViewPage() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [aggregate, setAggregate] = useState<TickerAggregation | null>(null);
  const [signal, setSignal] = useState<Signal | null>(null);
  const [articleTable, setArticleTable] = useState<TickerArticleTable | null>(null);

  useEffect(() => {
    void (async () => {
      const [aggregationData, signalData, articleData] = await Promise.all([
        getTickerAggregation(selectedTicker),
        getTickerSignal(selectedTicker),
        getTickerArticleTable(selectedTicker),
      ]);
      setAggregate(aggregationData);
      setSignal(signalData);
      setArticleTable(articleData);
    })();
  }, [selectedTicker]);

  const chartSeries = useMemo(() => {
    const base = aggregate?.avg_score ?? 0.5;
    return Array.from({ length: 12 }).map((_, index) => Math.min(0.95, Math.max(0.1, base + (index % 2 ? 0.03 : -0.02))));
  }, [aggregate]);

  return (
    <section>
      <PageHeader
        title="Ticker View"
        subtitle="Drill-down sentiment, ratios, and actionable signal by ticker"
        rightSlot={<TickerFilter options={WATCHLIST} selected={selectedTicker} onChange={setSelectedTicker} />}
      />

      <div className="panel-grid">
        <SentimentChart title={`${selectedTicker} sentiment curve`} values={chartSeries} />
        <article className="panel">
          <h3>Signal Snapshot</h3>
          {signal ? (
            <>
              <p>
                Signal: <strong>{signal.signal}</strong>
              </p>
              <p>Confidence: {(signal.confidence * 100).toFixed(1)}%</p>
              <p>{signal.rationale}</p>
            </>
          ) : (
            <p>Loading signal...</p>
          )}
        </article>
      </div>

      <article className="panel">
        <h3>Sentiment Composition</h3>
        {aggregate ? (
          <div className="ratio-row">
            <span>Positive {(aggregate.positive_ratio * 100).toFixed(0)}%</span>
            <span>Neutral {(aggregate.neutral_ratio * 100).toFixed(0)}%</span>
            <span>Negative {(aggregate.negative_ratio * 100).toFixed(0)}%</span>
            <span>Coverage {aggregate.article_count} items</span>
          </div>
        ) : (
          <p>Loading aggregation...</p>
        )}
      </article>

      <article className="panel">
        <h3>Article Score Table</h3>
        <table className="signals-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Source</th>
              <th>Label</th>
              <th>Score</th>
              <th>Confidence</th>
              <th>Preview</th>
            </tr>
          </thead>
          <tbody>
            {(articleTable?.rows ?? []).map((row) => (
              <tr key={row.sentiment_record_id}>
                <td>{new Date(row.timestamp).toLocaleTimeString()}</td>
                <td>{row.source}</td>
                <td>{row.label}</td>
                <td>{row.score.toFixed(2)}</td>
                <td>{(row.confidence * 100).toFixed(0)}%</td>
                <td>{row.text_preview}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}

export default TickerViewPage;
