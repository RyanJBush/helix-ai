from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.services.backtest_service import backtest_service

router = APIRouter()


@router.post("", response_model=BacktestResponse)
def run_backtest(payload: BacktestRequest, db: Session = Depends(get_db)) -> BacktestResponse:
    return backtest_service.run_backtest(db, payload)
