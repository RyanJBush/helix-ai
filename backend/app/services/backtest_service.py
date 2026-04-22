from datetime import datetime, timezone, time
from statistics import pstdev

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.sentiment import SentimentRecord
from app.schemas.backtest import (
    BacktestDayResult,
    BacktestRequest,
    BacktestResponse,
    ConfusionMatrix,
    PaperTradeDay,
    PaperTradeRequest,
    PaperTradeResponse,
    ThresholdCandidate,
    ThresholdTuningRequest,
    ThresholdTuningResponse,
)
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

    @staticmethod
    def _return_correlation(values_a: list[float], values_b: list[float]) -> float:
        if len(values_a) < 2 or len(values_b) < 2 or len(values_a) != len(values_b):
            return 0.0
        mean_a = sum(values_a) / len(values_a)
        mean_b = sum(values_b) / len(values_b)
        cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(values_a, values_b, strict=False))
        var_a = sum((a - mean_a) ** 2 for a in values_a)
        var_b = sum((b - mean_b) ** 2 for b in values_b)
        if var_a <= 0 or var_b <= 0:
            return 0.0
        return round(cov / ((var_a * var_b) ** 0.5), 4)

    @staticmethod
    def _proxy_intraday_move(weighted_score: float) -> float:
        return round(abs(weighted_score) * 0.015, 4)

    @staticmethod
    def _proxy_volatility_change(weighted_confidence: float, weighted_score: float) -> float:
        return round((1 - weighted_confidence) * 0.01 + abs(weighted_score) * 0.005, 4)

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
        now = datetime.now(timezone.utc).replace(tzinfo=None)

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
            next_day_return = round(weighted_score * 0.018, 4)
            intraday_move = self._proxy_intraday_move(weighted_score)
            volatility_change = self._proxy_volatility_change(weighted_confidence, weighted_score)
            benchmark_return = round(0.0005, 4)
            day_results.append(
                BacktestDayResult(
                    date=day,
                    weighted_sentiment_score=round(weighted_score, 4),
                    weighted_confidence=round(weighted_confidence, 4),
                    signal=signal.signal,
                    proxy_return=proxy_return,
                    next_day_return=next_day_return,
                    intraday_move=intraday_move,
                    volatility_change=volatility_change,
                    benchmark_return=benchmark_return,
                    relative_return=round(proxy_return - benchmark_return, 4),
                )
            )

        non_hold = [r for r in day_results if r.signal != "HOLD"]
        wins = [r for r in non_hold if (r.signal == "BUY" and r.proxy_return > 0) or (r.signal == "SELL" and r.proxy_return < 0)]
        returns = [r.proxy_return for r in non_hold]
        benchmark_returns = [r.benchmark_return for r in non_hold]
        relative_returns = [r.relative_return for r in non_hold]
        next_day_returns = [r.next_day_return for r in non_hold]
        cumulative = round(sum(returns), 4)
        cumulative_benchmark = round(sum(benchmark_returns), 4)
        cumulative_relative = round(sum(relative_returns), 4)
        volatility = pstdev(returns) if len(returns) > 1 else 0.0
        sharpe_like = round((sum(returns) / len(returns)) / volatility, 4) if returns and volatility > 0 else 0.0
        running = 0.0
        peak = 0.0
        max_drawdown = 0.0
        for item in non_hold:
            running += item.proxy_return
            peak = max(peak, running)
            max_drawdown = min(max_drawdown, running - peak)

        true_positive = len([r for r in non_hold if r.signal == "BUY" and r.proxy_return > 0])
        false_positive = len([r for r in non_hold if r.signal == "BUY" and r.proxy_return <= 0])
        true_negative = len([r for r in non_hold if r.signal == "SELL" and r.proxy_return < 0])
        false_negative = len([r for r in non_hold if r.signal == "SELL" and r.proxy_return >= 0])
        precision = round(true_positive / (true_positive + false_positive), 4) if (true_positive + false_positive) else 0.0
        recall = round(true_positive / (true_positive + false_negative), 4) if (true_positive + false_negative) else 0.0
        correlation = self._return_correlation(returns, next_day_returns)

        return BacktestResponse(
            ticker=ticker,
            period_start=payload.start_date,
            period_end=payload.end_date,
            total_days=(payload.end_date - payload.start_date).days + 1,
            trade_days=len(non_hold),
            hit_rate=round((len(wins) / len(non_hold)), 4) if non_hold else 0.0,
            precision=precision,
            recall=recall,
            cumulative_proxy_return=cumulative,
            cumulative_benchmark_return=cumulative_benchmark,
            cumulative_relative_return=cumulative_relative,
            max_drawdown=round(max_drawdown, 4),
            sharpe_like_ratio=sharpe_like,
            return_correlation=correlation,
            confusion_matrix=ConfusionMatrix(
                true_positive=true_positive,
                false_positive=false_positive,
                true_negative=true_negative,
                false_negative=false_negative,
            ),
            results=day_results,
        )

    def tune_thresholds(self, db: Session, payload: ThresholdTuningRequest) -> ThresholdTuningResponse:
        candidates: list[ThresholdCandidate] = []
        for buy in payload.buy_thresholds:
            for sell in payload.sell_thresholds:
                for min_conf in payload.min_confidences:
                    if sell >= 0 or buy <= 0:
                        continue
                    result = self.run_backtest(
                        db,
                        BacktestRequest(
                            ticker=payload.ticker,
                            start_date=payload.start_date,
                            end_date=payload.end_date,
                            buy_threshold=buy,
                            sell_threshold=sell,
                            min_confidence=min_conf,
                        ),
                    )
                    candidates.append(
                        ThresholdCandidate(
                            buy_threshold=buy,
                            sell_threshold=sell,
                            min_confidence=min_conf,
                            sharpe_like_ratio=result.sharpe_like_ratio,
                            hit_rate=result.hit_rate,
                            cumulative_proxy_return=result.cumulative_proxy_return,
                        )
                    )

        leaderboard = sorted(
            candidates,
            key=lambda row: (row.sharpe_like_ratio, row.hit_rate, row.cumulative_proxy_return),
            reverse=True,
        )
        best = leaderboard[0] if leaderboard else ThresholdCandidate(
            buy_threshold=0.25,
            sell_threshold=-0.25,
            min_confidence=0.45,
            sharpe_like_ratio=0.0,
            hit_rate=0.0,
            cumulative_proxy_return=0.0,
        )
        return ThresholdTuningResponse(
            ticker=payload.ticker.upper(),
            tested_candidates=len(candidates),
            best_candidate=best,
            leaderboard=leaderboard[:10],
        )

    def run_paper_trade(self, db: Session, payload: PaperTradeRequest) -> PaperTradeResponse:
        backtest = self.run_backtest(
            db,
            BacktestRequest(
                ticker=payload.ticker,
                start_date=payload.start_date,
                end_date=payload.end_date,
                buy_threshold=payload.buy_threshold,
                sell_threshold=payload.sell_threshold,
                min_confidence=payload.min_confidence,
            ),
        )
        cash = payload.initial_cash
        units = 0.0
        mark_price = 100.0
        trades = 0
        days: list[PaperTradeDay] = []

        for row in backtest.results:
            mark_price = max(10.0, mark_price * (1 + row.next_day_return))
            if row.signal == "BUY" and cash > 0:
                allocation = cash * payload.position_size
                bought = allocation / mark_price
                units += bought
                cash -= allocation
                trades += 1
            elif row.signal == "SELL" and units > 0:
                sold = units * payload.position_size
                units -= sold
                cash += sold * mark_price
                trades += 1

            portfolio_value = cash + units * mark_price
            days.append(
                PaperTradeDay(
                    date=row.date,
                    signal=row.signal,
                    cash=round(cash, 2),
                    position_units=round(units, 4),
                    mark_price=round(mark_price, 4),
                    portfolio_value=round(portfolio_value, 2),
                )
            )

        final_value = cash + units * mark_price
        return PaperTradeResponse(
            ticker=payload.ticker.upper(),
            initial_cash=round(payload.initial_cash, 2),
            final_cash=round(cash, 2),
            final_portfolio_value=round(final_value, 2),
            total_trades=trades,
            days=days,
        )


backtest_service = BacktestService()
