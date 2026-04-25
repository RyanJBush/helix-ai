from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    PaperTradeRequest,
    PaperTradeResponse,
    ScenarioBacktestResponse,
    ThresholdTuningRequest,
    ThresholdTuningResponse,
)
from app.services.backtest_service import backtest_service
from datetime import date

router = APIRouter()


@router.post("", response_model=BacktestResponse)
def run_backtest(payload: BacktestRequest, db: Session = Depends(get_db)) -> BacktestResponse:
    return backtest_service.run_backtest(db, payload)


@router.post("/tune", response_model=ThresholdTuningResponse)
def tune_thresholds(payload: ThresholdTuningRequest, db: Session = Depends(get_db)) -> ThresholdTuningResponse:
    return backtest_service.tune_thresholds(db, payload)


@router.post("/paper-trade", response_model=PaperTradeResponse)
def paper_trade(payload: PaperTradeRequest, db: Session = Depends(get_db)) -> PaperTradeResponse:
    return backtest_service.run_paper_trade(db, payload)


@router.get("/scenarios/{ticker}", response_model=ScenarioBacktestResponse)
def run_scenarios(
    ticker: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
) -> ScenarioBacktestResponse:
    return backtest_service.run_scenarios(db, ticker=ticker, start_date=start_date, end_date=end_date)
