import { useEffect, useState } from "react";
import { getAnalytics } from "../lib/api";
import type { Analytics as AnalyticsType } from "../lib/types";

function formatSeconds(seconds: number | null): string {
  if (seconds === null) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = seconds / 60;
  if (minutes < 60) return `${minutes.toFixed(1)} min`;
  return `${(minutes / 60).toFixed(1)} h`;
}

export default function Analytics() {
  const [data, setData] = useState<AnalyticsType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p style={{ color: "#dc2626" }}>{error}</p>;
  if (!data) return <p className="muted">Carregando…</p>;

  return (
    <div>
      <h1>Analytics</h1>
      <div className="cards-row">
        <div className="card">
          <div className="label">Total de tickets</div>
          <div className="value">{data.total_tickets}</div>
        </div>
        <div className="card">
          <div className="label">Resolvidos por IA</div>
          <div className="value">{data.resolved_by_ai_percent.toFixed(1)}%</div>
        </div>
        <div className="card">
          <div className="label">Tempo médio de resposta</div>
          <div className="value">{formatSeconds(data.avg_response_time_seconds)}</div>
        </div>
        <div className="card">
          <div className="label">Taxa de sucesso</div>
          <div className="value">{data.success_rate_percent.toFixed(1)}%</div>
        </div>
      </div>
      <p className="muted">
        Gráfico de volume por dia: adicione uma biblioteca de gráficos (ex: recharts) quando o
        endpoint de série temporal for implementado na Fase 2.
      </p>
    </div>
  );
}
