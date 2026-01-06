"""
Database Models for Flight Ticketing Kiosk System
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, 
    ForeignKey, Enum, create_engine
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class TicketStatus(PyEnum):
    """Status of a ticket."""
    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"


class Passenger(Base):
    """Passenger model - stores passenger information and face data reference."""
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    passport_number = Column(String(20), unique=True, nullable=False)
    face_file = Column(String(255), nullable=True)  # Path to encrypted face encoding
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="passenger", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Return full name of passenger."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Passenger(id={self.id}, name='{self.full_name}', passport='{self.passport_number}')>"


class Ticket(Base):
    """Ticket model - stores flight booking information."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(10), unique=True, nullable=False)  # e.g., "TK-A1B2C3"
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    
    # Flight details
    source_airport = Column(String(10), nullable=False)       # IATA code
    source_airport_name = Column(String(200), nullable=True)  # Full name
    destination_airport = Column(String(10), nullable=False)  # IATA code
    destination_airport_name = Column(String(200), nullable=True)  # Full name
    
    flight_date = Column(Date, nullable=False)
    flight_time = Column(Time, nullable=False)
    
    # Seat and gate (generated during check-in)
    seat_number = Column(String(5), nullable=True)   # e.g., "12A"
    gate = Column(String(5), nullable=True)          # e.g., "B7"
    
    # Status tracking
    status = Column(Enum(TicketStatus), default=TicketStatus.BOOKED)
    checked_in_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    passenger = relationship("Passenger", back_populates="tickets")
    
    def __repr__(self):
        return f"<Ticket(number='{self.ticket_number}', {self.source_airport}->{self.destination_airport}, status={self.status.value})>"


def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
