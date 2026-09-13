import { useEffect, useState } from "react";
import { approveTicket, listTickets, rejectTicket } from "../lib/api";
import type { Ticket, TicketStatus } from "../lib/types";
import TicketList from "./TicketList";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [status, setStatus] = useState<TicketStatus | "">("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listTickets({ status: status || undefined });
      setTickets(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  async function handleApprove(ticketId: string) {
    await approveTicket(ticketId);
    load();
  }

  async function handleReject(ticketId: string) {
    await rejectTicket(ticketId);
    load();
  }

  return (
    <div>
      <h1>Dashboard de Tickets</h1>

      <div className="filters">
        <select value={status} onChange={(e) => setStatus(e.target.value as TicketStatus | "")}>
          <option value="">Todos os status</option>
          <option value="open">Aberto</option>
          <option value="pending_approval">Aguardando aprovação</option>
          <option value="resolved">Resolvido</option>
          <option value="rejected">Rejeitado</option>
        </select>
        <button className="btn btn-secondary" onClick={load}>
          Atualizar
        </button>
      </div>

      {loading && <p className="muted">Carregando…</p>}
      {error && <p style={{ color: "#dc2626" }}>{error}</p>}
      {!loading && !error && (
        <TicketList tickets={tickets} onApprove={handleApprove} onReject={handleReject} />
      )}
    </div>
  );
}
