export default function NewsFeedPage({ news }) {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">News Feed</h2>
      <div className="space-y-3">
        {news.length === 0 && <p className="text-sm text-slate-400">No news articles yet.</p>}
        {news.map((article) => (
          <article key={article.id} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
            <p className="text-xs uppercase text-cyan-400">{article.ticker}</p>
            <h3 className="mt-1 text-lg font-medium">{article.title}</h3>
            <p className="mt-2 text-sm text-slate-300">{article.content}</p>
            <p className="mt-2 text-xs text-slate-500">Source: {article.source}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
