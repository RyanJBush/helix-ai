from fastapi import APIRouter

from app.schemas.replay import ReplayRequest, ReplayResponse
from app.services.replay_service import replay_service

router = APIRouter()


@router.post("", response_model=ReplayResponse)
def generate_replay(payload: ReplayRequest) -> ReplayResponse:
    return replay_service.generate(payload)
