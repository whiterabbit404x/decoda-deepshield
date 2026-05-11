import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function IntegrationsPage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Integrations</h2>
            <span className="badge">Connected Apps</span>
          </div>
          <p className="muted">Configure third-party workflows for SIEM, ticketing, identity, and notification systems.</p>
          <p className="muted">Integration health and credentials are managed through secure connectors.</p>
        </div>
      </section>
    </main>
  );
}
