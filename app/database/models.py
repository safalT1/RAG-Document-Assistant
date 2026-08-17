from datetime import datetime, date, time

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Time
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    pass


class DocumentMetadata(Base):

    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    chunk_strategy = Column(String(20), nullable=False)
    num_chunks = Column(Integer, nullable=False)
    embedding_dim = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class InterviewBooking(Base):
    __tablename__ = "interview_bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    interview_date = Column(Date, nullable=False)
    interview_time = Column(Time, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
