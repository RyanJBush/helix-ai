from fastapi import APIRouter

from app.api.v1.routers import analytics, backtesting, briefings, jobs, news, replay, sentiment, signals, streaming, trust

api_router = APIRouter()
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["backtesting"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
api_router.include_router(trust.router, prefix="/trust", tags=["trust"])
api_router.include_router(briefings.router, prefix="/briefings", tags=["briefings"])
api_router.include_router(replay.router, prefix="/replay", tags=["replay"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
