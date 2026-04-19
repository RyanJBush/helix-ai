from fastapi import APIRouter

from app.api.v1.routers import analytics, news, sentiment, signals, streaming

api_router = APIRouter()
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
