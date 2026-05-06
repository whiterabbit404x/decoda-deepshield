import { type DetectionOutput, type Incident } from "@/types/api";

interface DataTablesProps {
  detections: DetectionOutput[];
  incidents: Incident[];
  incidentsError?: string;
}

export function DataTables({ detections, incidents, incidentsError }: DataTablesProps) {
  return (
    <section className="tables-grid">
      <article className="card table-card">
        <h3>Recent Detections</h3>
        {detections.length === 0 ? <p className="state-text">No detections analyzed yet.</p> : null}
        {detections.length > 0 ? <ul>{detections.map((d) => <li key={d.id ?? d.label}>{d.label}</li>)}</ul> : null}
      </article>
      <article className="card table-card">
        <h3>Incidents</h3>
        {incidentsError ? <p className="state-text state-error">{incidentsError}</p> : null}
        {!incidentsError && incidents.length === 0 ? <p className="state-text">No incidents found.</p> : null}
        {!incidentsError && incidents.length > 0 ? <ul>{incidents.map((i) => <li key={i.id}>{`${i.id}  ${i.title}`}</li>)}</ul> : null}
      </article>
    </section>
  );
}
