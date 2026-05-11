import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function IncidentsPage() {
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
          <p className="muted">Use this view to monitor active incidents and route escalations.</p>
        </div>
      </section>
    </main>
  );
}
