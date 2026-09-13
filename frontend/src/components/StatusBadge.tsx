import type { TicketStatus } from "../lib/types";

const LABELS: Record<TicketStatus, string> = {
  open: "Aberto",
  pending_approval: "Aguardando aprovação",
  resolved: "Resolvido",
  rejected: "Rejeitado",
};

export default function StatusBadge({ status }: { status: TicketStatus }) {
  return <span className={`badge badge-${status}`}>{LABELS[status]}</span>;
}
