import type { Analytics, TicketDetail, TicketStatus, Ticket } from "./types";
import { getToken } from "./auth";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Erro ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function login(username: string, password: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error("Falha no login");
  }
  const data = (await res.json()) as { access_token: string };
  return data.access_token;
}

export function listTickets(filters: { status?: TicketStatus; date_from?: string; date_to?: string }) {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const qs = params.toString();
  return request<Ticket[]>(`/api/tickets${qs ? `?${qs}` : ""}`);
}

export function getTicket(ticketId: string) {
  return request<TicketDetail>(`/api/tickets/${ticketId}`);
}

export function approveTicket(ticketId: string) {
  return request<Ticket>(`/api/tickets/${ticketId}/approve`, { method: "POST" });
}

export function rejectTicket(ticketId: string) {
  return request<Ticket>(`/api/tickets/${ticketId}/reject`, { method: "POST" });
}

export function sendCustomResponse(ticketId: string, responseText: string) {
  return request<Ticket>(`/api/tickets/${ticketId}/custom-response`, {
    method: "POST",
    body: JSON.stringify({ response_text: responseText }),
  });
}

export function getAnalytics() {
  return request<Analytics>("/api/analytics");
}
