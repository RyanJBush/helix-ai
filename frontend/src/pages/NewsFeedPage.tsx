import { useEffect, useState } from 'react';

import PageHeader from '../components/PageHeader';
import TickerFilter from '../components/dashboard/TickerFilter';
import { WATCHLIST } from '../data/mockMarket';
import { ingestNews } from '../services/api';
import type { NewsItem } from '../types/market';

function NewsFeedPage() {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [news, setNews] = useState<NewsItem[]>([]);

  useEffect(() => {
    void (async () => {
      const rows = await ingestNews([selectedTicker]);
      setNews(rows);
    })();
  }, [selectedTicker]);

  return (
    <section>
      <PageHeader
        title="News Feed"
        subtitle="Streamlined market headlines feeding sentiment pipeline"
        rightSlot={<TickerFilter options={WATCHLIST} selected={selectedTicker} onChange={setSelectedTicker} />}
      />

      <article className="panel">
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
