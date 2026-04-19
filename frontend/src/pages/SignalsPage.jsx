export default function SignalsPage({ signal, ticker }) {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Signals</h2>
      {!ticker && <p className="text-sm text-slate-400">Select a ticker in Ticker View to inspect signals.</p>}
      {ticker && !signal && <p className="text-sm text-slate-400">No signal available for {ticker} yet.</p>}
      {signal && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <p className="text-xs uppercase text-cyan-400">{signal.ticker}</p>
          <p className="mt-1 text-xl font-semibold">{signal.signal}</p>
          <p className="mt-1 text-sm">Confidence: {signal.confidence.toFixed(3)}</p>
          <p className="mt-1 text-sm text-slate-300">{signal.reason}</p>
        </div>
      )}
    </section>
  )
}
