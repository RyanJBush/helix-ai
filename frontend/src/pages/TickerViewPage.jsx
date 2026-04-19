import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function TickerViewPage({ ticker, tickers, sentiment, signal, onTickerChange }) {
  const chartData = sentiment
    ? [
        {
          metric: 'Sentiment',
          value: sentiment.average_score,
        },
      ]
    : []

  return (
    <section className="space-y-6">
      <h2 className="text-2xl font-semibold">Ticker View</h2>
      <div className="max-w-sm">
        <label className="mb-2 block text-sm text-slate-300" htmlFor="ticker-select">
          Ticker Filter
        </label>
        <select
          className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2"
          id="ticker-select"
          value={ticker}
          onChange={(event) => onTickerChange(event.target.value)}
        >
          <option value="">Select ticker</option>
          {tickers.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Sentiment Snapshot</h3>
          {sentiment ? (
            <div className="space-y-1 text-sm">
              <p>Label: {sentiment.label}</p>
              <p>Average Score: {sentiment.average_score.toFixed(3)}</p>
              <p>Sample Size: {sentiment.sample_size}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">No sentiment data available for selected ticker.</p>
          )}
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-2 text-sm font-semibold text-slate-300">Trading Signal</h3>
          {signal ? (
            <div className="space-y-1 text-sm">
              <p>Signal: {signal.signal}</p>
              <p>Confidence: {signal.confidence.toFixed(3)}</p>
              <p>Reason: {signal.reason}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">No signal generated yet.</p>
          )}
        </div>
      </div>

      <div className="h-64 rounded-lg border border-slate-800 bg-slate-900 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
            <XAxis dataKey="metric" stroke="#94a3b8" />
            <YAxis domain={[-1, 1]} stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="value" fill="#38bdf8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
