import { type Alert } from "@/types/api";

interface AlertsListProps {
  alerts: Alert[];
  error?: string;
  loading?: boolean;
}

export function AlertsList({ alerts, error, loading }: AlertsListProps) {
  return (
    <article className="card alerts-card">
      <h3>Active Alerts</h3>
      {loading ? <p className="state-text">Loading alerts…</p> : null}
      {error ? <p className="state-text state-error">{error}</p> : null}
      {!loading && !error && alerts.length === 0 ? <p className="state-text">No active alerts.</p> : null}
      {!loading && !error && alerts.length > 0 ? (
        <ul>
          {alerts.map((alert) => (
            <li key={alert.id}>
              <span>{alert.title}</span>
              <strong>{alert.level}</strong>
            </li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}
