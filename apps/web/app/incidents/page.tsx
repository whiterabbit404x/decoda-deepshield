import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { getIncidents } from "@/lib/api";

export default async function IncidentsPage() {
  const [incidentsResult] = await Promise.allSettled([getIncidents()]);
  const incidents = incidentsResult.status === "fulfilled" ? incidentsResult.value : [];
  const incidentsError = incidentsResult.status === "rejected" ? incidentsResult.reason?.message ?? "Failed to load incidents." : undefined;

  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Incidents</h2>
            <span className="badge pri-medium">Open Queue</span>
          </div>
          <p className="muted">Review investigations, triage priorities, and current response assignments.</p>

          {incidentsError ? <p className="state-text state-error">{incidentsError}</p> : null}

          {!incidentsError && incidents.length === 0 ? (
            <p className="state-text">No incidents found. New incidents will appear here when detected.</p>
          ) : null}

          {!incidentsError && incidents.length > 0 ? (
            <ul>
              {incidents.map((incident) => (
                <li key={incident.incident_id}>
                  <div>
                    <span className={`badge pri-${incident.priority.toLowerCase()}`}>{incident.priority}</span>{" "}
                    <strong>{incident.summary}</strong>
                  </div>
                  <p className="muted">Incident #{incident.incident_id} · {incident.status}</p>
                  <small>{incident.created_at ? new Date(incident.created_at).toLocaleString() : "No timestamp"}</small>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </section>
    </main>
  );
}
