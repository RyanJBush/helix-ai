from datetime import UTC, datetime, time
from statistics import pstdev

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.schemas.backtest import BacktestDayResult, BacktestRequest, BacktestResponse
from app.services.signal_service import SignalThresholds, signal_service
from app.services.weighting_service import market_hours_multiplier, time_decay_multiplier


class BacktestService:
    @staticmethod
    def _label_to_direction(label: str) -> float:
        lowered = label.lower()
        if "pos" in lowered:
            return 1.0
        if "neg" in lowered:
            return -1.0
        return 0.0

    def run_backtest(self, db: Session, payload: BacktestRequest) -> BacktestResponse:
        ticker = payload.ticker.upper()
        start_dt = datetime.combine(payload.start_date, time.min)
        end_dt = datetime.combine(payload.end_date, time.max)

        rows = list(
            db.scalars(
                select(SentimentRecord).where(
                    and_(
                        SentimentRecord.ticker == ticker,
                        SentimentRecord.created_at >= start_dt,
                        SentimentRecord.created_at <= end_dt,
                    )
                )
            )
        )

        by_day: dict[datetime.date, list[SentimentRecord]] = {}
        for row in rows:
            by_day.setdefault(row.created_at.date(), []).append(row)

        day_results: list[BacktestDayResult] = []
        thresholds = SignalThresholds(
            buy_threshold=payload.buy_threshold,
            sell_threshold=payload.sell_threshold,
            min_confidence=payload.min_confidence,
        )
        now = datetime.now(UTC).replace(tzinfo=None)

        for day in sorted(by_day):
            records = by_day[day]
            weighted_sum = 0.0
            confidence_sum = 0.0
            total_weight = 0.0
            for row in records:
                weight = row.source_weight * market_hours_multiplier(row.created_at) * time_decay_multiplier(row.created_at, now=now)
                weighted_sum += self._label_to_direction(row.label) * row.score * weight
                confidence_sum += row.confidence * weight
                total_weight += weight

            weighted_score = weighted_sum / total_weight if total_weight else 0.0
            weighted_confidence = confidence_sum / total_weight if total_weight else 0.0
            aggregate_stub = type(
                "AggregateStub",
                (),
                {
                    "ticker": ticker,
                    "article_count": len(records),
                    "weighted_sentiment_score": round(weighted_score, 4),
                    "weighted_confidence": round(weighted_confidence, 4),
                },
            )()
            signal = signal_service.generate_from_aggregate(aggregate_stub, thresholds=thresholds)

            proxy_return = round(weighted_score * 0.02, 4)
            day_results.append(
                BacktestDayResult(
                    date=day,
                    weighted_sentiment_score=round(weighted_score, 4),
                    weighted_confidence=round(weighted_confidence, 4),
                    signal=signal.signal,
                    proxy_return=proxy_return,
                )
            )

        non_hold = [r for r in day_results if r.signal != "HOLD"]
        wins = [r for r in non_hold if (r.signal == "BUY" and r.proxy_return > 0) or (r.signal == "SELL" and r.proxy_return < 0)]
        returns = [r.proxy_return for r in non_hold]
        cumulative = round(sum(returns), 4)
        volatility = pstdev(returns) if len(returns) > 1 else 0.0
        sharpe_like = round((sum(returns) / len(returns)) / volatility, 4) if returns and volatility > 0 else 0.0

        return BacktestResponse(
            ticker=ticker,
            period_start=payload.start_date,
            period_end=payload.end_date,
            total_days=(payload.end_date - payload.start_date).days + 1,
            trade_days=len(non_hold),
            hit_rate=round((len(wins) / len(non_hold)), 4) if non_hold else 0.0,
            cumulative_proxy_return=cumulative,
            sharpe_like_ratio=sharpe_like,
            results=day_results,
        )


backtest_service = BacktestService()
