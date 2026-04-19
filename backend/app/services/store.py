from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.schemas import (
    AggregatedSentiment,
    DashboardSummary,
    NewsArticle,
    NewsArticleIn,
    SentimentRecord,
    TradingSignal,
)


class DataStore:
    def __init__(self) -> None:
        self.news_articles: list[NewsArticle] = []
        self.sentiment_scores: list[SentimentRecord] = []
        self.aggregated_sentiment: dict[str, AggregatedSentiment] = {}
        self.trading_signals: dict[str, TradingSignal] = {}

    def ingest(self, articles: list[NewsArticleIn]) -> list[NewsArticle]:
        ingested: list[NewsArticle] = []
        for article in articles:
            created = NewsArticle(
                id=str(uuid4()),
                ticker=article.ticker.upper(),
                source=article.source,
                title=article.title,
                content=article.content,
                created_at=datetime.now(UTC),
            )
            self.news_articles.append(created)
            ingested.append(created)
        return ingested

    def list_news(self, ticker: str | None = None, limit: int = 50) -> list[NewsArticle]:
        items = self.news_articles
        if ticker:
            ticker_upper = ticker.upper()
            items = [item for item in items if item.ticker == ticker_upper]
        return list(reversed(items[-limit:]))

    def add_sentiment(
        self,
        article: NewsArticle,
        score: float,
        label: str,
    ) -> SentimentRecord:
        record = SentimentRecord(
            article_id=article.id,
            ticker=article.ticker,
            score=score,
            label=label,  # type: ignore[arg-type]
            created_at=datetime.now(UTC),
        )
        self.sentiment_scores.append(record)
        self._update_aggregate(article.ticker)
        return record

    def _update_aggregate(self, ticker: str) -> None:
        ticker_records = [record for record in self.sentiment_scores if record.ticker == ticker]
        if not ticker_records:
            return

        average = sum(record.score for record in ticker_records) / len(ticker_records)
        if average > 0.2:
            sentiment_label = "positive"
        elif average < -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        aggregate = AggregatedSentiment(
            ticker=ticker,
            average_score=average,
            label=sentiment_label,  # type: ignore[arg-type]
            sample_size=len(ticker_records),
            updated_at=datetime.now(UTC),
        )
        self.aggregated_sentiment[ticker] = aggregate
        self.trading_signals[ticker] = self._build_signal(aggregate)

    @staticmethod
    def _build_signal(aggregate: AggregatedSentiment) -> TradingSignal:
        score = aggregate.average_score
        if score > 0.35:
            signal = "BUY"
            reason = "Sustained positive sentiment momentum"
        elif score < -0.35:
            signal = "SELL"
            reason = "Sustained negative sentiment pressure"
        else:
            signal = "HOLD"
            reason = "Sentiment remains mixed"

        return TradingSignal(
            ticker=aggregate.ticker,
            signal=signal,
            confidence=min(abs(score), 1.0),
            reason=reason,
            updated_at=datetime.now(UTC),
        )

    def get_sentiment(self, ticker: str) -> AggregatedSentiment | None:
        return self.aggregated_sentiment.get(ticker.upper())

    def get_signal(self, ticker: str) -> TradingSignal | None:
        return self.trading_signals.get(ticker.upper())

    def dashboard_summary(self) -> DashboardSummary:
        bullish = sum(1 for signal in self.trading_signals.values() if signal.signal == "BUY")
        bearish = sum(1 for signal in self.trading_signals.values() if signal.signal == "SELL")
        return DashboardSummary(
            total_articles=len(self.news_articles),
            analyzed_articles=len(self.sentiment_scores),
            tracked_tickers=len(self.aggregated_sentiment),
            bullish_tickers=bullish,
            bearish_tickers=bearish,
        )
