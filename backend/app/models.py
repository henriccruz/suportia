"""Modelos Pydantic usados nas requisições e respostas da API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database import TicketStatus, ResolutionType


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    customer_phone: str
    customer_name: Optional[str] = None
    message_text: str
    ai_response: Optional[str] = None
    manual_response: Optional[str] = None
    status: TicketStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_type: Optional[ResolutionType] = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: str
    ticket_id: str
    message_order: int
    is_customer: bool
    message_text: str
    timestamp: datetime


class TicketDetailOut(TicketOut):
    conversation: list[ConversationOut] = []


class CustomResponseIn(BaseModel):
    response_text: str


class AnalyticsOut(BaseModel):
    total_tickets: int
    resolved_by_ai_percent: float
    avg_response_time_seconds: Optional[float] = None
    success_rate_percent: float
