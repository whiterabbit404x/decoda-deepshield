import { type Alert } from "@/types/api";

interface AlertsListProps {
  alerts: Alert[];
  error?: string;
  loading?: boolean;
  onRetry: () => void;
}

export function AlertsList({ alerts, error, loading, onRetry }: AlertsListProps) {
  return (
    <article className="card alerts-card">
      <h3>Active Alerts</h3>
      {loading ? <p className="state-text">Loading alerts…</p> : null}
      {error ? <p className="state-text state-error">{error} <button className="link-btn" onClick={onRetry}>Reload panel</button></p> : null}
      {!loading && !error && alerts.length === 0 ? <p className="state-text">No active alerts.</p> : null}
      {!loading && !error && alerts.length > 0 ? (
        <ul>
          {alerts.map((alert) => (
            <li key={alert.alert_id}>
              <div>
                <span>{alert.recommended_action}</span>
                <p className="muted">{alert.created_at ? new Date(alert.created_at).toLocaleString() : "No timestamp"}</p>
              </div>
              <strong className={`badge pri-${alert.severity.toLowerCase()}`}>{alert.severity}</strong>
            </li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}
