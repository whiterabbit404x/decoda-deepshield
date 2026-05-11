import { type DetectionOutput, type Incident } from "@/types/api";

interface DataTablesProps {
  detections: DetectionOutput[];
  incidents: Incident[];
  incidentsError?: string;
  onRetryIncidents: () => void;
}

const truncate = (text: string, n = 72) => (text.length > n ? `${text.slice(0, n - 1)}…` : text);

export function DataTables({ detections, incidents, incidentsError, onRetryIncidents }: DataTablesProps) {
  return (
    <section className="tables-grid">
      <article className="card table-card">
        <h3>Recent Detections</h3>
        {detections.length === 0 ? <p className="state-text">No detections analyzed yet.</p> : (
          <ul>
            {detections.map((d) => (
              <li key={`${d.evidence_id}-${d.created_at}`}>
                <div><strong>{d.risk_level.toUpperCase()}</strong> · Score {d.synthetic_risk_score.toFixed(2)}</div>
                <p className="muted">Evidence ID: {d.evidence_id}</p>
                <p className="muted">Reasons: {truncate(d.reason_codes.join(", ") || "No reason codes")}</p>
                <p className="muted">Action: {truncate(d.recommended_action)}</p>
              </li>
            ))}
          </ul>
        )}
      </article>
      <article className="card table-card">
        <h3>Incidents</h3>
        {incidentsError ? <p className="state-text state-error">{incidentsError} <button className="link-btn" onClick={onRetryIncidents}>Reload panel</button></p> : null}
        {!incidentsError && incidents.length === 0 ? <p className="state-text">No incidents found.</p> : null}
        {!incidentsError && incidents.length > 0 ? <ul>{incidents.map((i) => <li key={i.incident_id}><div><span className={`badge sev-${i.priority.toLowerCase()}`}>{i.priority}</span> <strong>{i.summary}</strong></div><p className="muted">{truncate(i.status)}</p><small>{i.created_at ? new Date(i.created_at).toLocaleString() : "No timestamp"}</small></li>)}</ul> : null}
      </article>
    </section>
  );
}
