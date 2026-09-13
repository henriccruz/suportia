"""Definição de todos os endpoints da API."""
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.claude_service import generate_response
from app.database import (
    Conversation,
    ResolutionType,
    Ticket,
    TicketStatus,
    get_db,
)
from app.models import AnalyticsOut, CustomResponseIn, TicketDetailOut, TicketOut
from app.twilio_service import send_message

router = APIRouter(prefix="/api")


def _next_message_order(db: Session, ticket_id: str) -> int:
    last = (
        db.query(func.max(Conversation.message_order))
        .filter(Conversation.ticket_id == ticket_id)
        .scalar()
    )
    return (last or 0) + 1


@router.post("/messages/webhook")
async def messages_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Recebe o webhook de mensagem do Twilio (SMS/WhatsApp) e responde automaticamente."""
    phone_number = From
    message_text = Body
    received_at = datetime.now(timezone.utc)

    ticket = db.query(Ticket).filter(Ticket.customer_phone == phone_number).first()

    if ticket is None or ticket.status in (TicketStatus.RESOLVED, TicketStatus.REJECTED):
        # Cliente novo, ou reabrindo conversa após um ticket já encerrado.
        if ticket is not None:
            db.delete(ticket)
            db.flush()
        ticket = Ticket(
            customer_phone=phone_number,
            customer_name=ProfileName,
            message_text=message_text,
            status=TicketStatus.PENDING_APPROVAL,
            created_at=received_at,
        )
        db.add(ticket)
        db.flush()
    else:
        ticket.message_text = message_text
        ticket.status = TicketStatus.PENDING_APPROVAL

    ai_response = generate_response(message_text, customer_name=ticket.customer_name)
    ticket.ai_response = ai_response

    order = _next_message_order(db, ticket.ticket_id)
    db.add(Conversation(
        ticket_id=ticket.ticket_id,
        message_order=order,
        is_customer=True,
        message_text=message_text,
        timestamp=received_at,
    ))
    db.add(Conversation(
        ticket_id=ticket.ticket_id,
        message_order=order + 1,
        is_customer=False,
        message_text=ai_response,
        timestamp=datetime.now(timezone.utc),
    ))

    db.commit()

    # Responde imediatamente ao cliente via TwiML (auto-resposta do Twilio).
    twiml = f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{ai_response}</Message></Response>"
    return Response(content=twiml, media_type="application/xml")


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    status: Optional[TicketStatus] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Lista os últimos 100 tickets, com filtros opcionais por status e data."""
    query = db.query(Ticket)

    if status is not None:
        query = query.filter(Ticket.status == status)
    if date_from is not None:
        query = query.filter(Ticket.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Ticket.created_at <= date_to)

    tickets = query.order_by(Ticket.created_at.desc()).limit(100).all()
    return tickets


@router.get("/tickets/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")

    conversation = (
        db.query(Conversation)
        .filter(Conversation.ticket_id == ticket_id)
        .order_by(Conversation.message_order.asc())
        .all()
    )
    result = TicketDetailOut.model_validate(ticket)
    result.conversation = conversation
    return result


def _get_ticket_or_404(db: Session, ticket_id: str) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket


@router.post("/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Aprova a resposta da IA, marca o ticket como resolvido e envia a resposta final ao cliente."""
    ticket = _get_ticket_or_404(db, ticket_id)
    if not ticket.ai_response:
        raise HTTPException(status_code=400, detail="Ticket não possui resposta de IA para aprovar")

    ticket.status = TicketStatus.RESOLVED
    ticket.resolution_type = ResolutionType.AI_APPROVED
    ticket.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)

    send_message(ticket.customer_phone, ticket.ai_response)
    return ticket


@router.post("/tickets/{ticket_id}/reject", response_model=TicketOut)
def reject_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Rejeita a resposta da IA e marca o ticket para revisão manual."""
    ticket = _get_ticket_or_404(db, ticket_id)
    ticket.status = TicketStatus.REJECTED
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/tickets/{ticket_id}/custom-response", response_model=TicketOut)
def custom_response(ticket_id: str, payload: CustomResponseIn, db: Session = Depends(get_db)):
    """Permite que o agente envie uma resposta customizada e marque o ticket como resolvido."""
    ticket = _get_ticket_or_404(db, ticket_id)
    ticket.manual_response = payload.response_text
    ticket.status = TicketStatus.RESOLVED
    ticket.resolution_type = ResolutionType.MANUAL
    ticket.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)

    send_message(ticket.customer_phone, payload.response_text)
    return ticket


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)):
    total_tickets = db.query(func.count(Ticket.ticket_id)).scalar() or 0

    resolved_by_ai = (
        db.query(func.count(Ticket.ticket_id))
        .filter(Ticket.resolution_type.in_([ResolutionType.AI_AUTO, ResolutionType.AI_APPROVED]))
        .scalar()
        or 0
    )

    resolved_total = (
        db.query(func.count(Ticket.ticket_id))
        .filter(Ticket.status == TicketStatus.RESOLVED)
        .scalar()
        or 0
    )

    # NOTA: julianday() é específico do SQLite. Ao migrar para PostgreSQL,
    # troque por EXTRACT(EPOCH FROM (resolved_at - created_at)).
    avg_seconds = (
        db.query(func.avg(func.julianday(Ticket.resolved_at) - func.julianday(Ticket.created_at)))
        .filter(Ticket.resolved_at.isnot(None))
        .scalar()
    )
    avg_response_time_seconds = avg_seconds * 86400 if avg_seconds is not None else None

    resolved_by_ai_percent = (resolved_by_ai / total_tickets * 100) if total_tickets else 0.0
    success_rate_percent = (resolved_total / total_tickets * 100) if total_tickets else 0.0

    return AnalyticsOut(
        total_tickets=total_tickets,
        resolved_by_ai_percent=round(resolved_by_ai_percent, 2),
        avg_response_time_seconds=avg_response_time_seconds,
        success_rate_percent=round(success_rate_percent, 2),
    )
