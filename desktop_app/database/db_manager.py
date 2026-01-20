"""
Database Manager for Flight Ticketing Kiosk System
Handles database connections, sessions, and CRUD operations.
"""
import random
import string
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_URL, init_directories
from database.models import Base, Passenger, Ticket, TicketStatus, create_tables


class DatabaseManager:
    """Manages database connections and provides CRUD operations."""
    
    def __init__(self):
        """Initialize database connection."""
        init_directories()
        self.engine = create_engine(DATABASE_URL, echo=False)
        create_tables(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== Passenger Operations ====================
    
    def create_passenger(
        self,
        first_name: str,
        last_name: str,
        passport_number: str,
        face_file: Optional[str] = None
    ) -> Passenger:
        """Create a new passenger."""
        with self.get_session() as session:
            passenger = Passenger(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                passport_number=passport_number.strip().upper(),
                face_file=face_file
            )
            session.add(passenger)
            session.flush()
            session.refresh(passenger)
            # Detach from session to return
            session.expunge(passenger)
            return passenger
    
    def get_passenger_by_id(self, passenger_id: int) -> Optional[Passenger]:
        """Get a passenger by ID."""
        with self.get_session() as session:
            passenger = session.query(Passenger).filter(Passenger.id == passenger_id).first()
            if passenger:
                session.expunge(passenger)
            return passenger
    
    def get_passenger_by_passport(self, passport_number: str) -> Optional[Passenger]:
        """Get a passenger by passport number."""
        with self.get_session() as session:
            passenger = session.query(Passenger).filter(
                Passenger.passport_number == passport_number.strip().upper()
            ).first()
            if passenger:
                session.expunge(passenger)
            return passenger
    
    def get_all_passengers(self) -> List[Passenger]:
        """Get all passengers."""
        with self.get_session() as session:
            passengers = session.query(Passenger).all()
            for p in passengers:
                session.expunge(p)
            return passengers
    
    def update_passenger_face(self, passenger_id: int, face_file: str) -> bool:
        """Update passenger's face file path."""
        with self.get_session() as session:
            passenger = session.query(Passenger).filter(Passenger.id == passenger_id).first()
            if passenger:
                passenger.face_file = face_file
                return True
            return False
    
    # ==================== Ticket Operations ====================
    
    @staticmethod
    def generate_ticket_number() -> str:
        """Generate a unique ticket number like TK-A1B2C3."""
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=6))
        return f"TK-{code}"
    
    @staticmethod
    def generate_seat() -> str:
        """Generate a random seat number like 12A."""
        row = random.randint(1, 30)
        seat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
        return f"{row}{seat}"
    
    @staticmethod
    def generate_gate() -> str:
        """Generate a random gate like B7."""
        terminal = random.choice(['A', 'B', 'C', 'D'])
        gate_num = random.randint(1, 20)
        return f"{terminal}{gate_num}"
    
    def create_ticket(
        self,
        passenger_id: int,
        source_airport: str,
        source_airport_name: str,
        destination_airport: str,
        destination_airport_name: str,
        flight_date,
        flight_time
    ) -> Ticket:
        """Create a new ticket for a passenger."""
        with self.get_session() as session:
            ticket = Ticket(
                ticket_number=self.generate_ticket_number(),
                passenger_id=passenger_id,
                source_airport=source_airport.upper(),
                source_airport_name=source_airport_name,
                destination_airport=destination_airport.upper(),
                destination_airport_name=destination_airport_name,
                flight_date=flight_date,
                flight_time=flight_time,
                status=TicketStatus.BOOKED
            )
            session.add(ticket)
            session.flush()
            session.refresh(ticket)
            session.expunge(ticket)
            return ticket
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID."""
        with self.get_session() as session:
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket:
                session.expunge(ticket)
            return ticket
    
    def get_ticket_by_number(self, ticket_number: str) -> Optional[Ticket]:
        """Get a ticket by ticket number."""
        with self.get_session() as session:
            ticket = session.query(Ticket).filter(
                Ticket.ticket_number == ticket_number.strip().upper()
            ).first()
            if ticket:
                session.expunge(ticket)
            return ticket
    
    def get_tickets_by_passenger(self, passenger_id: int) -> List[Ticket]:
        """Get all tickets for a passenger."""
        with self.get_session() as session:
            tickets = session.query(Ticket).filter(
                Ticket.passenger_id == passenger_id
            ).order_by(Ticket.flight_date.desc()).all()
            for t in tickets:
                session.expunge(t)
            return tickets
    
    def get_all_tickets(self) -> List[Ticket]:
        """Get all tickets with passenger info."""
        with self.get_session() as session:
            tickets = session.query(Ticket).order_by(Ticket.created_at.desc()).all()
            for t in tickets:
                session.expunge(t)
            return tickets
    
    def get_booked_tickets(self) -> List[Ticket]:
        """Get all tickets that are booked but not checked in."""
        with self.get_session() as session:
            tickets = session.query(Ticket).filter(
                Ticket.status == TicketStatus.BOOKED
            ).order_by(Ticket.flight_date).all()
            for t in tickets:
                session.expunge(t)
            return tickets
    
    def check_in_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Check in a ticket - generate seat, gate, update status."""
        with self.get_session() as session:
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket and ticket.status == TicketStatus.BOOKED:
                ticket.seat_number = self.generate_seat()
                ticket.gate = self.generate_gate()
                ticket.status = TicketStatus.CHECKED_IN
                ticket.checked_in_at = datetime.utcnow()
                session.flush()
                session.refresh(ticket)
                session.expunge(ticket)
                return ticket
            return None
    
    def cancel_ticket(self, ticket_id: int) -> bool:
        """Cancel a ticket."""
        with self.get_session() as session:
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket and ticket.status != TicketStatus.CANCELLED:
                ticket.status = TicketStatus.CANCELLED
                return True
            return False
    
    def reset_ticket_checkin(self, ticket_id: int) -> bool:
        """Reset a ticket's check-in status (admin function)."""
        with self.get_session() as session:
            ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
            if ticket and ticket.status == TicketStatus.CHECKED_IN:
                ticket.status = TicketStatus.BOOKED
                ticket.seat_number = None
                ticket.gate = None
                ticket.checked_in_at = None
                return True
            return False
    
    def delete_passenger(self, passenger_id: int) -> bool:
        """Delete a passenger and all their tickets (cascade)."""
        with self.get_session() as session:
            passenger = session.query(Passenger).filter(Passenger.id == passenger_id).first()
            if passenger:
                session.delete(passenger)
                return True
            return False
            
    def cleanup_old_checkins(self) -> int:
        """
        Reset tickets that were checked in more than 24 hours ago.
        Returns the number of tickets reset.
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        with self.get_session() as session:
            old_tickets = session.query(Ticket).filter(
                Ticket.status == TicketStatus.CHECKED_IN,
                Ticket.checked_in_at <= cutoff
            ).all()
            
            count = 0
            for ticket in old_tickets:
                ticket.status = TicketStatus.BOOKED
                ticket.seat_number = None
                ticket.gate = None
                ticket.checked_in_at = None
                count += 1
            
            return count


# Global database instance
db = DatabaseManager()
