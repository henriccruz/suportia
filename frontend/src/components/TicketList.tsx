import { Link } from "react-router-dom";
import type { Ticket } from "../lib/types";
import StatusBadge from "./StatusBadge";

interface Props {
  tickets: Ticket[];
  onApprove: (ticketId: string) => void;
  onReject: (ticketId: string) => void;
}

function truncate(text: string, max = 80) {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

export default function TicketList({ tickets, onApprove, onReject }: Props) {
  if (tickets.length === 0) {
    return <p className="muted">Nenhum ticket encontrado.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Cliente</th>
          <th>Mensagem</th>
          <th>Resposta IA</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        {tickets.map((ticket) => (
          <tr key={ticket.ticket_id}>
            <td>
              <Link to={`/tickets/${ticket.ticket_id}`}>{ticket.ticket_id.slice(0, 8)}</Link>
            </td>
            <td>{ticket.customer_name ? `${ticket.customer_name} (${ticket.customer_phone})` : ticket.customer_phone}</td>
            <td>{truncate(ticket.message_text)}</td>
            <td>{ticket.ai_response ? truncate(ticket.ai_response) : <span className="muted">—</span>}</td>
            <td>
              <StatusBadge status={ticket.status} />
            </td>
            <td>
              <Link className="btn btn-secondary" to={`/tickets/${ticket.ticket_id}`}>
                Ver
              </Link>
              {ticket.status === "pending_approval" && (
                <>
                  <button className="btn btn-success" onClick={() => onApprove(ticket.ticket_id)}>
                    Aprovar
                  </button>
                  <button className="btn btn-danger" onClick={() => onReject(ticket.ticket_id)}>
                    Rejeitar
                  </button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
