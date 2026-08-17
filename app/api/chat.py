import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.services.rag import rag_pipeline
from app.services.booking import save_booking_from_detection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        result = rag_pipeline(
            session_id=request.session_id,
            query=request.query,
        )

   
        booking_info = None
        if result.get("booking"):
            saved = save_booking_from_detection(db, result["booking"])
            if saved:
                booking_info = {
                    "id": saved.id,
                    "name": saved.name,
                    "email": saved.email,
                    "date": str(saved.interview_date),
                    "time": str(saved.interview_time),
                }
                logger.info("Auto-saved booking #%d from chat", saved.id)

        return ChatResponse(
            session_id=request.session_id,
            query=request.query,
            answer=result["answer"],
            sources=result.get("sources", []),
            booking=booking_info,
        )

    except Exception as exc:
        logger.exception("Chat failed for session '%s'", request.session_id)
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}")