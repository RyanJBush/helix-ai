import { useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import NavBar from './components/NavBar.jsx'
import {
  connectStream,
  fetchNews,
  fetchSummary,
  fetchTickerSentiment,
  fetchTickerSignal,
  ingestSimulatedNews,
  runSentimentAnalysis,
} from './api.js'
import DashboardPage from './pages/DashboardPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import NewsFeedPage from './pages/NewsFeedPage.jsx'
import SignalsPage from './pages/SignalsPage.jsx'
import TickerViewPage from './pages/TickerViewPage.jsx'

const defaultSummary = {
  total_articles: 0,
  analyzed_articles: 0,
  tracked_tickers: 0,
  bullish_tickers: 0,
  bearish_tickers: 0,
}

function App() {
  const [summary, setSummary] = useState(defaultSummary)
  const [news, setNews] = useState([])
  const [ticker, setTicker] = useState('')
  const [tickerSentiment, setTickerSentiment] = useState(null)
  const [tickerSignal, setTickerSignal] = useState(null)

  const tickers = useMemo(() => [...new Set(news.map((item) => item.ticker))].sort(), [news])
  const sentimentSeries = useMemo(() => {
    if (!tickerSentiment || !ticker) {
      return []
    }
    return [{ ticker, score: tickerSentiment.average_score }]
  }, [ticker, tickerSentiment])

  const refreshAllData = async () => {
    const [summaryData, newsData] = await Promise.all([fetchSummary(), fetchNews()])
    setSummary(summaryData)
    setNews(newsData)
  }

  useEffect(() => {
    const bootstrap = async () => {
      await ingestSimulatedNews(8)
      await runSentimentAnalysis()
      await refreshAllData()
    }

    bootstrap()
  }, [])

  useEffect(() => {
    if (!ticker) {
      return
    }

    const loadTickerData = async () => {
      const [sentiment, signal] = await Promise.all([
        fetchTickerSentiment(ticker),
        fetchTickerSignal(ticker),
      ])
      setTickerSentiment(sentiment)
      setTickerSignal(signal)
    }

    loadTickerData()
  }, [ticker])

  useEffect(() => {
    const ws = connectStream((event) => {
      if (event?.event === 'summary' && event.payload) {
        setSummary((current) => ({ ...current, ...event.payload }))
      }
      if (event?.event === 'news_ingested' || event?.event === 'sentiment_updated') {
        refreshAllData()
      }
    })

    return () => ws.close()
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <NavBar />
      <main className="mx-auto w-full max-w-6xl p-4 sm:p-6">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <DashboardPage
                summary={summary}
                sentimentSeries={sentimentSeries}
                onRefresh={refreshAllData}
              />
            }
          />
          <Route
            path="/ticker"
            element={
              <TickerViewPage
                ticker={ticker}
                tickers={tickers}
                sentiment={tickerSentiment}
                signal={tickerSignal}
                onTickerChange={setTicker}
              />
            }
          />
          <Route path="/news" element={<NewsFeedPage news={news} />} />
          <Route path="/signals" element={<SignalsPage signal={tickerSignal} ticker={ticker} />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
