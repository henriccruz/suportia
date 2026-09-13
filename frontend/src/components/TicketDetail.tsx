import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { approveTicket, getTicket, rejectTicket, sendCustomResponse } from "../lib/api";
import type { TicketDetail as TicketDetailType } from "../lib/types";
import StatusBadge from "./StatusBadge";

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<TicketDetailType | null>(null);
  const [customResponse, setCustomResponse] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!id) return;
    setLoading(true);
    try {
      const data = await getTicket(id);
      setTicket(data);
      setCustomResponse(data.manual_response ?? "");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleApprove() {
    if (!id) return;
    setSubmitting(true);
    try {
      await approveTicket(id);
      await load();
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject() {
    if (!id) return;
    setSubmitting(true);
    try {
      await rejectTicket(id);
      await load();
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSendCustom() {
    if (!id || !customResponse.trim()) return;
    setSubmitting(true);
    try {
      await sendCustomResponse(id, customResponse.trim());
      await load();
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="muted">Carregando…</p>;
  if (error) return <p style={{ color: "#dc2626" }}>{error}</p>;
  if (!ticket) return null;

  const canAct = ticket.status === "pending_approval" || ticket.status === "rejected";

  return (
    <div>
      <button className="btn btn-secondary" onClick={() => navigate(-1)}>
        ← Voltar
      </button>

      <h1 style={{ marginBottom: 4 }}>
        Ticket {ticket.ticket_id.slice(0, 8)} <StatusBadge status={ticket.status} />
      </h1>
      <p className="muted">
        Cliente: {ticket.customer_name ? `${ticket.customer_name} (${ticket.customer_phone})` : ticket.customer_phone}
      </p>

      <div className="card" style={{ marginTop: 16, marginBottom: 16 }}>
        <h3>Histórico de Conversa</h3>
        {ticket.conversation.length === 0 && <p className="muted">Sem histórico de conversa.</p>}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 8,
            maxHeight: 400,
            overflowY: "auto",
          }}
        >
          {ticket.conversation.map((msg) => (
            <div key={msg.conversation_id} style={{ display: "flex", gap: 8 }}>
              <div
                style={{
                  flexShrink: 0,
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  background: msg.is_customer ? "#dbeafe" : "#dcfce7",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                {msg.is_customer ? "C" : "IA"}
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: 12, color: "#6b7280", margin: "0 0 4px 0" }}>
                  {msg.is_customer ? "Cliente" : "IA"} • {new Date(msg.timestamp).toLocaleTimeString("pt-BR")}
                </p>
                <p style={{ margin: 0, fontSize: 14, lineHeight: 1.4, whiteSpace: "pre-wrap" }}>
                  {msg.message_text}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {ticket.manual_response && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Resposta manual enviada</h3>
          <p>{ticket.manual_response}</p>
        </div>
      )}

      {canAct && (
        <div className="card">
          <h3>Ações</h3>
          {ticket.ai_response && (
            <div style={{ marginBottom: 16 }}>
              <button className="btn btn-success" disabled={submitting} onClick={handleApprove}>
                Aprovar resposta IA
              </button>
              <button className="btn btn-danger" disabled={submitting} onClick={handleReject}>
                Rejeitar
              </button>
            </div>
          )}

          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 6 }}>
            Resposta customizada
          </label>
          <textarea
            value={customResponse}
            onChange={(e) => setCustomResponse(e.target.value)}
            placeholder="Escreva uma resposta manual para o cliente…"
          />
          <div style={{ marginTop: 8 }}>
            <button
              className="btn btn-primary"
              disabled={submitting || !customResponse.trim()}
              onClick={handleSendCustom}
            >
              Enviar e resolver
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
