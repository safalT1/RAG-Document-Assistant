import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.request import BookingRequest
from app.schemas.response import BookingResponse, BookingListResponse
from app.services.booking import create_booking, get_all_bookings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=BookingResponse)
def book_interview(
    request: BookingRequest,
    db: Session = Depends(get_db),
) -> BookingResponse:
 
    try:
        booking = create_booking(
            db=db,
            name=request.name,
            email=request.email,
            interview_date=request.date,
            interview_time=request.time,
            notes=request.notes,
        )
        return BookingResponse(
            id=booking.id,
            name=booking.name,
            email=booking.email,
            date=str(booking.interview_date),
            time=str(booking.interview_time),
            notes=booking.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Booking creation failed")
        raise HTTPException(status_code=500, detail=f"Booking failed: {exc}")


@router.get("/", response_model=BookingListResponse)
def list_bookings(
    db: Session = Depends(get_db),
) -> BookingListResponse:
#List all interview bookings
    bookings = get_all_bookings(db)
    return BookingListResponse(
        bookings=[
            BookingResponse(
                id=b.id,
                name=b.name,
                email=b.email,
                date=str(b.interview_date),
                time=str(b.interview_time),
                notes=b.notes,
            )
            for b in bookings
        ]
    )
