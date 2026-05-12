import { type Alert, type HealthResponse, type Incident, type RuntimeStatus } from "@/types/api";

export interface StatCardProps {
  label: string;
  value: string;
  delta: string;
  direction: "up" | "down";
  status: "good" | "warning" | "critical" | "neutral";
}

interface StatCardsProps {
  health?: HealthResponse | null;
  runtimeStatus?: RuntimeStatus | null;
  alerts: Alert[];
  incidents: Incident[];
}

export function StatCard({ label, value, delta, direction, status }: StatCardProps) {
  return (
    <article className={`card stat-card status-${status}`}>
      <p className="muted">{label}</p>
      <h3>{value}</h3>
      <p className={`delta delta-${direction}`}>
        <span aria-hidden>{direction === "up" ? "↗" : "↘"}</span> {delta}
      </p>
    </article>
  );
}

export function StatCards({ health, runtimeStatus, alerts, incidents }: StatCardsProps) {
  const lastSyncAt = runtimeStatus?.last_sync_at;
  const formattedLastSync = lastSyncAt
    ? new Date(lastSyncAt).toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short"
      })
    : "Unavailable";

  const stats: StatCardProps[] = [
    { label: "Threats Blocked", value: `${runtimeStatus?.alert_count ?? alerts.length}`, delta: "8% vs prior period", direction: "up", status: "good" },
    {
      label: "Active Incidents",
      value: `${runtimeStatus?.incident_count ?? incidents.length}`,
      delta: incidents.length > 0 ? "Requires response" : "No active response",
      direction: incidents.length > 0 ? "up" : "down",
      status: incidents.length > 4 ? "critical" : incidents.length > 0 ? "warning" : "good"
    },
    {
      label: "API Status",
      value: runtimeStatus?.api_status ?? health?.status ?? "Offline",
      delta: health?.service ?? "Connectivity issue",
      direction: (runtimeStatus?.api_status ?? health?.status)?.toLowerCase() === "ok" ? "up" : "down",
      status: (runtimeStatus?.api_status ?? health?.status)?.toLowerCase() === "ok" ? "good" : "critical"
    },
    {
      label: "Last Sync",
      value: formattedLastSync,
      delta: "Realtime feed",
      direction: "up",
      status: "neutral"
    }
  ];

  return <section className="stats-grid">{stats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>;
}
