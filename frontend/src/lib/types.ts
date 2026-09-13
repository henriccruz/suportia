export type TicketStatus = "open" | "pending_approval" | "resolved" | "rejected";
export type ResolutionType = "ai_auto" | "ai_approved" | "manual";

export interface Ticket {
  ticket_id: string;
  customer_phone: string;
  customer_name: string | null;
  message_text: string;
  ai_response: string | null;
  manual_response: string | null;
  status: TicketStatus;
  created_at: string;
  resolved_at: string | null;
  resolution_type: ResolutionType | null;
}

export interface ConversationMessage {
  conversation_id: string;
  ticket_id: string;
  message_order: number;
  is_customer: boolean;
  message_text: string;
  timestamp: string;
}

export interface TicketDetail extends Ticket {
  conversation: ConversationMessage[];
}

export interface Analytics {
  total_tickets: number;
  resolved_by_ai_percent: number;
  avg_response_time_seconds: number | null;
  success_rate_percent: number;
}
