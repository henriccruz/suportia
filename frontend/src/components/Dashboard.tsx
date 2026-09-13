import { useEffect, useState } from "react";
import { approveTicket, listTickets, rejectTicket } from "../lib/api";
import type { Ticket, TicketStatus } from "../lib/types";
import TicketList from "./TicketList";

export default function Dashboard() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [status, setStatus] = useState<TicketStatus | "">("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await listTickets({ status: status || undefined });
      setTickets(
        data.filter((t) =>
          search
            ? t.customer_phone.includes(search) ||
              t.customer_name?.toLowerCase().includes(search.toLowerCase())
            : true,
        ),
      );
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

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(load, 5000);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRefresh]);

  async function handleApprove(ticketId: string) {
    await approveTicket(ticketId);
    load();
  }

  async function handleReject(ticketId: string) {
    await rejectTicket(ticketId);
    load();
  }

  const pendingCount = tickets.filter((t) => t.status === "pending_approval").length;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Dashboard de Tickets</h1>
        {pendingCount > 0 && (
          <span
            className="badge badge-pending_approval"
            style={{ fontSize: 12, padding: "4px 8px" }}
          >
            {pendingCount} aguardando aprovação
          </span>
        )}
      </div>

      <div className="filters">
        <select value={status} onChange={(e) => setStatus(e.target.value as TicketStatus | "")}>
          <option value="">Todos os status</option>
          <option value="open">Aberto</option>
          <option value="pending_approval">Aguardando aprovação</option>
          <option value="resolved">Resolvido</option>
          <option value="rejected">Rejeitado</option>
        </select>

        <input
          type="text"
          placeholder="Buscar por nome ou telefone…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <label style={{ marginLeft: 12, fontSize: 13, display: "flex", alignItems: "center" }}>
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            style={{ marginRight: 4 }}
          />
          Auto-atualizar a cada 5s
        </label>

        <button className="btn btn-secondary" onClick={load}>
          Atualizar agora
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
