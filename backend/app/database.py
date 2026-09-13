"""Configuração do SQLAlchemy: engine, sessão e modelos ORM."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum, Integer, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# SQLite precisa desse argumento extra para funcionar com múltiplas threads (FastAPI usa um pool de threads).
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    PENDING_APPROVAL = "pending_approval"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ResolutionType(str, enum.Enum):
    AI_AUTO = "ai_auto"
    AI_APPROVED = "ai_approved"
    MANUAL = "manual"


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_phone = Column(String(32), unique=True, nullable=False, index=True)
    customer_name = Column(String(120), nullable=True)
    message_text = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    manual_response = Column(Text, nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING_APPROVAL, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_type = Column(Enum(ResolutionType), nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    message_order = Column(Integer, nullable=False)
    is_customer = Column(Boolean, nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(80), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
