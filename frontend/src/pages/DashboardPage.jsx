import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

function KpiCard({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <p className="text-xs uppercase text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-cyan-300">{value}</p>
    </div>
  )
}

export default function DashboardPage({ summary, sentimentSeries, onRefresh }) {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <button
          className="rounded bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950"
          onClick={onRefresh}
          type="button"
        >
          Refresh Data
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard label="News Articles" value={summary.total_articles} />
        <KpiCard label="Analyzed" value={summary.analyzed_articles} />
        <KpiCard label="Tickers" value={summary.tracked_tickers} />
        <KpiCard label="Bullish" value={summary.bullish_tickers} />
        <KpiCard label="Bearish" value={summary.bearish_tickers} />
      </div>

      <div className="h-72 rounded-lg border border-slate-800 bg-slate-900 p-4">
        <h3 className="mb-3 text-sm font-medium text-slate-300">Sentiment Trend by Ticker</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sentimentSeries}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
            <XAxis dataKey="ticker" stroke="#94a3b8" />
            <YAxis domain={[-1, 1]} stroke="#94a3b8" />
            <Tooltip />
            <Line type="monotone" dataKey="score" stroke="#22d3ee" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
