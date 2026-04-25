import { useEffect, useState } from 'react';

import PageHeader from '../components/PageHeader';
import TickerFilter from '../components/dashboard/TickerFilter';
import { WATCHLIST } from '../data/mockMarket';
import { ingestAndScore, ingestNews } from '../services/api';
import type { IngestAndScoreSummary, NewsItem } from '../types/market';

function NewsFeedPage() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [news, setNews] = useState<NewsItem[]>([]);
  const [pipelineSummary, setPipelineSummary] = useState<IngestAndScoreSummary | null>(null);

  useEffect(() => {
    void (async () => {
      const rows = await ingestNews([selectedTicker]);
      setNews(rows);
    })();
  }, [selectedTicker]);

  const runPipeline = async () => {
    const summary = await ingestAndScore([selectedTicker]);
    setPipelineSummary(summary);
    const rows = await ingestNews([selectedTicker]);
    setNews(rows);
  };

  return (
    <section>
      <PageHeader
        title="News Feed"
        subtitle="Streamlined market headlines feeding sentiment pipeline"
        rightSlot={<TickerFilter options={WATCHLIST} selected={selectedTicker} onChange={setSelectedTicker} />}
      />

      <article className="panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.8rem' }}>
          <h3>Ingestion Feed</h3>
          <button type="button" className="action-button" onClick={() => void runPipeline()}>
            Run ingest → sentiment → signal
          </button>
        </div>
        {pipelineSummary ? (
          <p className="muted" style={{ marginTop: '0.6rem' }}>
            Run {pipelineSummary.run_id}: {pipelineSummary.news_items_inserted} news, {pipelineSummary.sentiments_created} sentiments,{' '}
            {pipelineSummary.signals_created} signals
          </p>
        ) : null}
        <ul className="news-list">
          {news.map((item, index) => (
            <li key={`${item.ticker}-${index}`}>
              <div>
                <strong>{item.ticker}</strong>
                <span className="muted"> • {item.source}</span>
              </div>
              <h4>{item.headline}</h4>
              <p>{item.content}</p>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}

export default NewsFeedPage;
