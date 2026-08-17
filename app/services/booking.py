import logging
from datetime import date, time, datetime
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.database.models import InterviewBooking

logger = logging.getLogger(__name__)


def create_booking(
    db: Session,
    name: str,
    email: str,
    interview_date: str,
    interview_time: str,
    notes: Optional[str] = None,
) -> InterviewBooking:
    
    booking = InterviewBooking(
        name=name,
        email=email,
        interview_date=date.fromisoformat(interview_date),
        interview_time=time.fromisoformat(interview_time),
        notes=notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    logger.info("Created booking #%d for %s <%s>", booking.id, name, email)
    return booking


def get_all_bookings(db: Session) -> List[InterviewBooking]:
    
    return db.query(InterviewBooking).order_by(InterviewBooking.created_at.desc()).all()


def save_booking_from_detection(
    db: Session,
    booking_data: Dict,
) -> Optional[InterviewBooking]:
    
    try:
        return create_booking(
            db=db,
            name=booking_data["name"],
            email=booking_data["email"],
            interview_date=booking_data["date"],
            interview_time=booking_data["time"],
        )
    except Exception as exc:
        logger.warning("Could not auto-save detected booking: %s", exc)
        return None
