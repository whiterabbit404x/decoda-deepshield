import { type Alert, type HealthResponse, type Incident } from "@/types/api";

interface StatCardsProps {
  health?: HealthResponse | null;
  alerts: Alert[];
  incidents: Incident[];
}

export function StatCards({ health, alerts, incidents }: StatCardsProps) {
  const stats = [
    { label: "Threats Blocked", value: `${alerts.length}`, delta: "Live" },
    { label: "Active Incidents", value: `${incidents.length}`, delta: incidents.length > 0 ? "Needs triage" : "Stable" },
    { label: "API Status", value: health?.status ?? "Offline", delta: health?.service ?? "Connectivity issue" },
    { label: "Last Sync", value: health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : "Unavailable", delta: "No cache" }
  ];

  return (
    <section className="stats-grid">
      {stats.map((stat) => (
        <article key={stat.label} className="card stat-card">
          <p className="muted">{stat.label}</p>
          <h3>{stat.value}</h3>
          <p className="delta">{stat.delta}</p>
        </article>
      ))}
    </section>
  );
}
