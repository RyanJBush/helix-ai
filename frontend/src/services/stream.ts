import type { StreamEvent } from '../types/market';

const STREAM_BASE = import.meta.env.VITE_STREAM_URL ?? 'ws://localhost:8000/api/v1/streaming/ws';

const MOCK_TICKERS = ['AAPL', 'MSFT', 'TSLA', 'NVDA'];

export function connectStream(onMessage: (data: StreamEvent) => void): WebSocket {
  const socket = new WebSocket(STREAM_BASE);
  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      onMessage({ event: 'stream_text', payload: event.data, timestamp: new Date().toISOString() });
    }
  };
  return socket;
}

export function startMockStream(onMessage: (data: StreamEvent) => void): () => void {
  const timer = setInterval(() => {
    const ticker = MOCK_TICKERS[Math.floor(Math.random() * MOCK_TICKERS.length)];
    const score = Number((Math.random() * 0.5 + 0.35).toFixed(2));
    onMessage({
      event: 'sentiment_update',
      ticker,
      score,
      label: score > 0.65 ? 'positive' : score < 0.45 ? 'negative' : 'neutral',
      timestamp: new Date().toISOString(),
    });
  }, 2500);

  return () => clearInterval(timer);
}
